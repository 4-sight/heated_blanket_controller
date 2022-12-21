import uasyncio as asyncio
from store import PicoStore
from display import Display
from connection import Connection


async def main():

    store = PicoStore()
    display = Display()
    connection = Connection(store, display)
    connection.connect()
    asyncio.create_task(connection.monitor_connection())

    while True:
        await asyncio.sleep(5)
        print("tick")

try:
    asyncio.run(main())
finally:
    asyncio.new_event_loop()
