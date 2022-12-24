from network import WLAN
from secrets import secrets
import uasyncio as asyncio
import rp2
import network
import time
from actions import ACTIONS
from logger import Logger

ssid = secrets['ssid']
password = secrets['pw']


class Connection:
    _wlan: WLAN
    _logger: Logger

    def __init__(self, publisher, logger) -> None:
        rp2.country('EN')
        self._wlan = WLAN(network.STA_IF)
        self._wlan.active(True)
        self._logger = logger
        self._publish = publisher

    def connect(self) -> None:
        self._publish(ACTIONS.WIFI_CONNECTING, None)
        self._wlan.connect(ssid, password)

        timeout = 10
        while timeout > 0:
            if self._wlan.status() < 0 or self._wlan.status() >= 3:
                break
            timeout -= 1
            self._logger.log('log', 'Waiting for connection...')
            time.sleep(1)

        if self._wlan.status() != 3:
            self._publish(ACTIONS.WIFI_CONNECTION_FAILED, self._wlan.status())
        else:
            self._publish(ACTIONS.WIFI_CONNECTED, self._wlan.ifconfig())

    async def monitor_connection(self):
        while True:
            await asyncio.sleep(20)
            self._logger.log('debug', 'checking connection status...')

            if self._wlan.status() != 3:
                self._logger.log('warn', 'Connection lost')
                self.connect()
            else:
                self._logger.log('debug', 'Connection healthy')
