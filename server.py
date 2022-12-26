import json
from events import Events, ACTIONS
import uasyncio as asyncio


class Server:
    _events: Events

    def __init__(self, events: Events) -> None:
        self._events = events

    async def start(self):
        self._events.publish(ACTIONS.LOG_DEBUG, "Setting up webserver...")
        asyncio.create_task(asyncio.start_server(
            self._serve_client, "0.0.0.0", 80))
        self._events.publish(ACTIONS.LOG_VERBOSE, "Server listening...")

    async def _serve_client(self, reader, writer):
        self._events.publish(ACTIONS.CLIENT_CONNECTED, None)

        req_buffer = await reader.read(4096)
        req = parse_http_request(req_buffer)

        method = req['method']
        route: str = req['path']
        self._events.publish(ACTIONS.LOG_DEBUG, route)

        # GET
        if method == "GET":

            if route.startswith("/app"):
                await serve_app(writer)

            else:
                await serve_public_asset(writer, route)

        if method == "POST":
            if route == "/api/apply_preset/":
                # print(req['body'])
                body = json.loads(req['body'])
                payload = {'preset': body['preset']}
                self._events.publish(ACTIONS.APPLY_PRESET, payload)

                writer.write(
                    'HTTP/1.1 200 OK\r\nContent-type: text/html\r\n\r\n')

        await writer.drain()
        await writer.wait_closed()
        self._events.publish(ACTIONS.CLIENT_DISCONNECTED, None)


# =============================================================


async def serve_app(writer):
    path = "./dist/index.html"
    with open(path, 'r') as file:
        html = file.read()

    writer.write('HTTP/1.1 200 OK\r\nContent-type: text/html\r\n\r\n')
    writer.write(html)


# =============================================================

async def serve_public_asset(writer, path: str):
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
            writer.write('HTTP/1.1 500 Bad Request\r\n')
    except:
        writer.write('HTTP/1.1 404 Bad Request\r\n')

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
