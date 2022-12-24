import uasyncio as asyncio
from app import App


async def main():
    app = App()
    app.setup()
    asyncio.create_task(app.start())

    await app.run()

try:
    asyncio.run(main())
finally:
    asyncio.new_event_loop()
