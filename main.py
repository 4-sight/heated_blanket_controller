import uasyncio as asyncio


async def main():

    while True:
        await asyncio.sleep(5)

try:
    asyncio.run(main())
finally:
    asyncio.new_event_loop()
