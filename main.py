import uasyncio as asyncio
from store import PicoStore
from display import Display
from connection import Connection
from server import Server
from control import Control


async def main():

    display = Display()
    store = PicoStore(display)
    connection = Connection(store, display)
    server = Server(store, display)
    control = Control(store, display)

    connection.connect()
    asyncio.create_task(server.start())
    asyncio.create_task(connection.monitor_connection())

    while True:
        await asyncio.sleep(5)

try:
    asyncio.run(main())
finally:
    asyncio.new_event_loop()
