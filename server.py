import json
from actions import ACTIONS
from store import PicoStore
from display import Display
import uasyncio as asyncio


class Server:
    _store: PicoStore
    _display: Display

    def __init__(self, store: PicoStore, display: Display) -> None:
        self._store = store
        self._display = display

    async def start(self):
        self._display.display_message("Setting up webserver...")
        asyncio.create_task(asyncio.start_server(
            self._serve_client, "0.0.0.0", 80))
        self._display.display_message("Server listening...")

    async def _serve_client(self, reader, writer):
        self._store.publish(ACTIONS.CLIENT_CONNECTED)

        req_buffer = await reader.read(4096)
        req = parse_http_request(req_buffer)

        method = req['method']
        route: str = req['path']

        # GET
        if method == "GET":

            if route.startswith("/public"):
                await serve_public_asset(writer, route)

            elif route == "/":
                await serve_page(writer, "home")

            elif route in [
                "/control_onboard",
                "/control_external_led",
                "/404"
            ]:
                await serve_page(writer, route.replace('/', ''))

            else:
                await serve_page(writer, "404")

        if method == "POST":
            if route == "/api/onboard_led/":
                # print(req['body'])
                body = json.loads(req['body'])

                self._store.set_state("onboard_led", body['led'])

                writer.write(
                    'HTTP/1.1 200 OK\r\nContent-type: text/html\r\n\r\n')

            if route == "/api/external_led_pulse/":
                # print(req['body'])
                body = json.loads(req['body'])

                if 'rate' in body:
                    rate = int(body['rate'])
                    self._store.set_state("pulse_led", rate)

                writer.write(
                    'HTTP/1.1 200 OK\r\nContent-type: text/html\r\n\r\n')

            if route == "/api/stop_pulse/":
                self._store.publish(ACTIONS.PULSE_STOP)

                writer.write(
                    'HTTP/1.1 200 OK\r\nContent-type: text/html\r\n\r\n')

        await writer.drain()
        await writer.wait_closed()
        self._store.publish(ACTIONS.CLIENT_DISCONNECTED)


# =============================================================


def get_html(page_name):
    path = "./pages/" + page_name + ".html"
    with open(path, 'r') as file:
        html = file.read()

    return html

# =============================================================


async def serve_page(writer, page_name):
    html = get_html(page_name)

    writer.write('HTTP/1.1 200 OK\r\nContent-type: text/html\r\n\r\n')
    writer.write(html)


# =============================================================

async def serve_public_asset(writer, path: str):
    asset = open("." + path)
    response = asset.read()

    if path.find(".css") > 0:
        writer.write('HTTP/1.1 200 OK\r\nContent-type: text/css\r\n\r\n')
        writer.write(response)
    elif path.find(".js") > 0:
        writer.write(
            'HTTP/1.1 200 OK\r\nContent-type: text/javascript\r\n\r\n')
        writer.write(response)
    elif path.find(".ico") > 0:
        writer.write('HTTP/1.1 200 OK\r\nContent-type: image/x-icon\r\n\r\n')
        writer.write(response)
    elif path.find(".png") > 0:
        writer.write('HTTP/1.1 200 OK\r\nContent-type: image/png\r\n\r\n')
        writer.write(response)

# =============================================================

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
