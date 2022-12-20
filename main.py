import uasyncio as asyncio
from display import display_message


async def main():

    display_message("Running...")

    while True:
        await asyncio.sleep(5)

try:
    asyncio.run(main())
finally:
    asyncio.new_event_loop()
