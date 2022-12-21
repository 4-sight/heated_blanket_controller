from network import WLAN
from secrets import secrets
import uasyncio as asyncio
import rp2
import network
import time
from store import PicoStore, ACTIONS
from display import Display

ssid = secrets['ssid']
password = secrets['pw']


class Connection:
    _wlan: WLAN
    _store: PicoStore
    _display: Display

    def __init__(self, store: PicoStore, display: Display) -> None:
        rp2.country('EN')
        self._wlan = WLAN(network.STA_IF)
        self._wlan.active(True)
        self._store = store
        self._display = display

    def connect(self) -> None:
        self._display.display_message('Connecting to wi-fi...')
        self._store.publish(ACTIONS.WIFI_CONNECTING)
        self._wlan.connect(ssid, password)

        timeout = 10
        while timeout > 0:
            if self._wlan.status() < 0 or self._wlan.status() >= 3:
                break
            timeout -= 1
            self._display.display_message('Waiting for connection...')
            time.sleep(1)

        if self._wlan.status() != 3:
            self._display.display_message('Wi-fi connection failed')
            self._store.publish(ACTIONS.WIFI_CONNECTION_FAILED)
        else:
            self._ip = self._wlan.ifconfig()[0]
            self._display.display_message(
                'Wi-fi connected\n''Ip: {}'.format(self._ip))
            self._store.publish(ACTIONS.WIFI_CONNECTED)

    async def monitor_connection(self):
        while True:
            await asyncio.sleep(20)
            self._display.display_message('checking connection status...')

            if self._wlan.status() != 3:
                self._display.display_message('Connection lost')
                self.connect()
            else:
                self._display.display_message('Connection healthy')
