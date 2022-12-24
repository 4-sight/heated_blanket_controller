from logger import Logger
import uasyncio as asyncio
from actions import ACTIONS
from machine import Pin
from pimoroni import Button


class Inputs:
    _logger: Logger

    def __init__(self, publisher, logger) -> None:
        self._logger = logger
        self._publish = publisher
        self.buttons = {
            'a': Button(12, repeat_time=500, hold_time=2000),
            'b': Button(13, repeat_time=500, hold_time=2000),
            'x': Button(14, repeat_time=500, hold_time=2000),
            'y': Button(15, repeat_time=500, hold_time=2000)
        }

    async def listen(self) -> None:
        self._logger.log('debug', 'listening for inputs...')

        while True:
            for button in self.buttons.values():
                if button.read():
                    self._publish(ACTIONS.BUTTON_PRESSED,
                                  payload=self.buttons)

            await asyncio.sleep(0.1)
