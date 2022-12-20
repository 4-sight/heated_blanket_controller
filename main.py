import uasyncio as asyncio

from secrets import secrets
from network_connect import connect_to_wifi

ssid = secrets['ssid']
password = secrets['pw']


async def main():

    connect_to_wifi(ssid, password)

    while True:
        await asyncio.sleep(5)

try:
    asyncio.run(main())
finally:
    asyncio.new_event_loop()
