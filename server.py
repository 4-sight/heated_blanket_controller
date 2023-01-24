import json
from control import Control
from logger import Logger
from events import Events, ACTIONS
import uasyncio as asyncio
import gc


class Server:
    _events: Events
    _logger: Logger

    def __init__(self, events: Events, control: Control, logger: Logger) -> None:
        self._events = events
        self._logger = logger
        self._control = control

    def start(self):
        self._events.publish(ACTIONS.LOG_DEBUG, "Setting up webserver...")
        asyncio.create_task(asyncio.start_server(
            self._serve_client, "0.0.0.0", 80))
        self._events.publish(ACTIONS.LOG_VERBOSE, "Server listening...")

    async def _serve_client(self, reader, writer):
        self._events.publish(ACTIONS.CLIENT_CONNECTED, None)

        req_buffer = None
        req = None
        method = None
        route = ""
        data = None
        response = None
        body = None
        payload = None

        try:
            req_buffer = await reader.read(4096)
            req = parse_http_request(req_buffer)

            method = req['method']
            route: str = req['path']
            self._events.publish(ACTIONS.LOG_DEBUG, route)

            # GET
            if method == "GET":

                if route.startswith("/app"):
                    await serve_app(writer)

                elif route.startswith("/drain_logs"):
                    data = self._control.take_channel_logs()
                    response = json.dumps(data)
                    writer.write(
                        'HTTP/1.1 200 OK\r\nContent-type: application/json\r\n\r\n')
                    writer.write(response)
                elif route.startswith("/curve_data/1"):
                    curve_data = self._control.get_curve_data(1)
                    response = json.dumps(curve_data)
                    writer.write(
                        'HTTP/1.1 200 OK\r\nContent-type: application/json\r\n\r\n')
                    writer.write(response)
                elif route.startswith("/curve_data/2"):
                    data = self._control.get_curve_data(2)
                    response = json.dumps(data)
                    writer.write(
                        'HTTP/1.1 200 OK\r\nContent-type: application/json\r\n\r\n')
                    writer.write(response)
                elif route.startswith("/heater_levels"):
                    data = self._control.get_heater_levels()
                    response = json.dumps(data)
                    writer.write(
                        'HTTP/1.1 200 OK\r\nContent-type: application/json\r\n\r\n')
                    writer.write(response)
                elif route.startswith("/logging_level"):
                    data = self._logger.get_level()
                    response = json.dumps({'level': data})
                    writer.write(
                        'HTTP/1.1 200 OK\r\nContent-type: application/json\r\n\r\n')
                    writer.write(response)
                else:
                    await serve_public_asset(writer, route)

            if method == "POST":
                if route == "/api/apply_preset/":
                    body = json.loads(req['body'])
                    payload = int(body['preset'])
                    self._events.publish(ACTIONS.APPLY_PRESET, payload)

                    writer.write(
                        'HTTP/1.1 200 OK\r\nContent-type: text/html\r\n\r\n')

                elif route == "/api/set_heater_levels/":
                    body = json.loads(req['body'])
                    payload = body['heater_levels']
                    self._events.publish(ACTIONS.SET_LEVELS, payload)

                    writer.write(
                        'HTTP/1.1 200 OK\r\nContent-type: text/html\r\n\r\n')

                elif route == "/api/adjust_safety_range/":
                    body = json.loads(req['body'])
                    payload = body['safety_range_settings']
                    self._events.publish(ACTIONS.ADJUST_SAFETY_RANGE, payload)

                    writer.write(
                        'HTTP/1.1 200 OK\r\nContent-type: text/html\r\n\r\n')

                elif route == "/api/set_logging_level/":
                    body = json.loads(req['body'])
                    payload = body['log_level']
                    self._logger._set_level(payload)

                    writer.write(
                        'HTTP/1.1 200 OK\r\nContent-type: text/html\r\n\r\n')

        except MemoryError:
            writer.write('HTTP/1.1 503 Out of Resources\r\n\r\n')
        finally:
            await writer.drain()
            await writer.wait_closed()
            self._events.publish(ACTIONS.CLIENT_DISCONNECTED, None)
            del req_buffer
            del req
            del method
            del route
            del data
            del response
            del body
            del payload
            gc.collect()

# =============================================================


async def serve_app(writer):
    path = "./dist/index.html"
    file = None
    html = None

    try:
        with open(path, 'r') as file:
            html = file.read()

        writer.write('HTTP/1.1 200 OK\r\nContent-type: text/html\r\n\r\n')
        writer.write(html)
    except MemoryError:
        writer.write('HTTP/1.1 503 Out of Resources\r\n\r\n')
    finally:
        del file
        del html
        del path
        gc.collect()


# =============================================================

async def serve_public_asset(writer, path: str):
    asset = None
    response = None
    try:
        asset = open("./dist" + path)
        response = asset.read()

        if path.find(".css") > 0:
            writer.write('HTTP/1.1 200 OK\r\nContent-type: text/css\r\n\r\n')
            writer.write(response)
        elif path.find(".js") > 0:
            writer.write(
                'HTTP/1.1 200 OK\r\nContent-type: text/javascript\r\n\r\n')
            writer.write(response)
        elif path.find(".ico") > 0:
            writer.write(
                'HTTP/1.1 200 OK\r\nContent-type: image/x-icon\r\n\r\n')
            writer.write(response)
        elif path.find(".png") > 0:
            writer.write('HTTP/1.1 200 OK\r\nContent-type: image/png\r\n\r\n')
            writer.write(response)
        elif path.find(".svg") > 0:
            writer.write(
                'HTTP/1.1 200 OK\r\nContent-type: image/svg+xml\r\n\r\n')
            writer.write(response)
        else:
            print("unhandled file type")
            writer.write('HTTP/1.1 415 Unsupported Media Type\r\n')
    except MemoryError:
        writer.write('HTTP/1.1 503 Out of Resources\r\n\r\n')
    except Exception as ex:
        print("ERROR: Failed to serve asset", ex)
        writer.write('HTTP/1.1 500 Server Error\r\n\r\n')
        writer.write("ERROR: Failed to serve asset \r\n{}\r\n".format(ex))
    finally:
        del asset
        del response
        gc.collect()

# =============================================================


def parse_http_request(req_buffer):
    req = {}
    req_buffer_lines = req_buffer.decode('utf8').split('\r\n')
    req['method'], target, req['http_version'] = req_buffer_lines[0].split(
        ' ', 2)  # Example: GET /route/path HTTP/1.1
    if (not '?' in target):
        req['path'] = target
    else:  # target can have a query component, so /route/path could be something like /route/path?state=on&timeout=30
        req['path'], query_string = target.split('?', 1)
        req['query'] = parse_query_string(query_string)

    req['headers'] = {}
    for i in range(1, len(req_buffer_lines) - 1):
        # Blank line signifies the end of headers.
        if (req_buffer_lines[i] == ''):
            break
        else:
            name, value = req_buffer_lines[i].split(':', 1)
            req['headers'][name.strip()] = value.strip()

    # Last line is the body (or blank if no body.)
    req['body'] = req_buffer_lines[len(req_buffer_lines) - 1]

    del target
    del req_buffer_lines
    del req_buffer

    gc.collect()

    return req

# =============================================================


def parse_query_string(query_string):
    query = {}
    query_params = query_string.split('&')
    for param in query_params:
        if (not '=' in param):  # Example: somebody sent ?on instead of ?state=on
            key = param
            query[key] = ''
        else:
            key, value = param.split('=')
            query[key] = value

    return query
