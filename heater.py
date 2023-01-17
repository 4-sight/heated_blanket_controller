from machine import Pin
import uasyncio as asyncio
from uasyncio import Task
from events import Events, ACTIONS
import time

ZONE_STATUS_INITIAL = 0
ZONE_STATUS_OK = 3
ZONE_STATUS_ERROR_SAFETY_LOW = -1
ZONE_STATUS_ERROR_SAFETY_HIGH = -2
ZONE_STATUS_ERROR_CHANNEL_ERROR = -3


class Heater:
    name: str
    _events: Events
    _level: int
    _output: Pin
    _running: Task | None = None
    __status__: int
    is_live: bool
    _output_timestamp: int

    def __init__(self, name: str, output: Pin, events: Events) -> None:
        self._events = events
        self._level = 0
        self.name = name
        self._output = output
        self.__status__ = ZONE_STATUS_INITIAL
        self.is_live = False
        self._output_timestamp = 0

    def set_status(self, statusCode) -> None:
        self.__status__ = statusCode

    def get_status(self) -> int:
        return self.__status__

    def set_level(self, level: int) -> None:
        if self.__status__ < ZONE_STATUS_OK:
            self._events.publish(
                ACTIONS.LOG_ERROR, "ZONE SET LEVEL IGNORED, invalid zone status")
            return

        self._level = level

        if self._running != None:
            self._running.cancel()

        async def run():
            if self._level <= 0:
                self._turn_off()
                return

            while True:
                level = self._level
                self._events.publish(
                    ACTIONS.LOG_INFO, self.name + " on")
                self._turn_on()
                await asyncio.sleep(level)

                if level < 10:
                    self._events.publish(
                        ACTIONS.LOG_INFO, self.name + " off")
                    self._turn_off()
                    await asyncio.sleep(10 - level)

        self._running = asyncio.create_task(run())

    def _set_output_timestamp(self) -> None:
        self._output_timestamp = time.ticks_ms()

    def get_output_timestamp(self) -> int:
        return self._output_timestamp

    def _turn_on(self) -> None:
        self._output.value(1)

        if self.is_live == False:
            self._set_output_timestamp()
        self.is_live = True

    def _turn_off(self) -> None:
        self._output.value(0)

        if self.is_live == True:
            self._set_output_timestamp()
        self.is_live = False

    def clear(self) -> None:
        self._turn_off()
        self._level = 0
        if self._running != None:
            self._running.cancel()
        self._running = None

    async def energise(self, duration=0.1):
        if self.__status__ < ZONE_STATUS_INITIAL:
            self._events.publish(
                ACTIONS.LOG_ERROR, "ZONE ENERGISE ABORTED, invalid zone status")
            return

        self.clear()
        self._output.value(1)
        self.is_live = True
        self._events.publish(ACTIONS.HEATER_ENERGISED, self.name)
        await asyncio.sleep(duration)
        self._turn_off()
