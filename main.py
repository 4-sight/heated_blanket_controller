import uasyncio as asyncio
from store import PicoStore
from display import Display
from connection import Connection
from server import serve_client


async def main():

    store = PicoStore()
    display = Display()
    connection = Connection(store, display)
    connection.connect()

    display.display_message("Setting up webserver...")
    server = serve_client(store, display)
    asyncio.create_task(asyncio.start_server(server, "0.0.0.0", 80))
    display.display_message("Server listening...")
    asyncio.create_task(connection.monitor_connection())

    while True:
        await asyncio.sleep(5)

try:
    asyncio.run(main())
finally:
    asyncio.new_event_loop()
