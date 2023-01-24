from machine import Pin
import uasyncio as asyncio
from uasyncio import Task
from events import Events, ACTIONS
import time
import math

ZONE_STATUS_INITIAL = 0
ZONE_STATUS_OK = 3
ZONE_STATUS_ERROR_SAFETY_LOW = -1
ZONE_STATUS_ERROR_SAFETY_HIGH = -2
ZONE_STATUS_ERROR_CHANNEL_ERROR = -3


class Heater:
    name: str
    is_live: bool
    _A: float
    _B: float
    _C: int
    _events: Events
    _level: int
    _output: Pin
    _running: Task | None = None
    _charge: float
    _res_charge: float
    _state_change_timestamp: int
    __status__: int

    def __init__(self, name: str, output: Pin, events: Events, A: float, B: float, C: int) -> None:
        self._events = events
        self._level = 0
        self.name = name
        self._output = output
        self.__status__ = ZONE_STATUS_INITIAL
        self.is_live = False
        self._state_change_timestamp = 0
        self._A = A
        self._B = B
        self._C = C
        self._charge = 0
        self._res_charge = 0

    def set_status(self, statusCode) -> None:
        self.__status__ = statusCode

    def get_status(self) -> int:
        return self.__status__

    def get_level(self) -> int:
        return self._level

    def set_level(self, level: int) -> None:
        if self.__status__ < ZONE_STATUS_OK:
            self._events.publish(
                ACTIONS.LOG_ERROR, "ZONE SET LEVEL IGNORED, invalid zone status")
            return

        self._level = level % 10

        if self._running != None:
            self._running.cancel()

        async def run():
            if self._level <= 0:
                self._turn_off()
                return

            while True:
                self._events.publish(
                    ACTIONS.LOG_INFO, self.name + " on")
                self._turn_on()
                await asyncio.sleep(self._level)

                if level < 10:
                    self._events.publish(
                        ACTIONS.LOG_INFO, self.name + " off")
                    self._turn_off()
                    await asyncio.sleep(10 - self._level)

        self._running = asyncio.create_task(run())

    def _set_state_change_timestamp(self) -> None:
        self._state_change_timestamp = time.ticks_ms()

    def get_state_change_timestamp(self) -> int:
        return self._state_change_timestamp

    def _toggle_state(self) -> None:
        self._set_state_change_timestamp()
        self._res_charge = self._charge
        self.is_live = not self.is_live

    def _turn_on(self) -> None:
        self._output.value(1)
        if self.is_live == False:
            self._toggle_state()

    def _turn_off(self) -> None:
        self._output.value(0)
        if self.is_live == True:
            self._toggle_state()

    def clear(self) -> None:
        self._turn_off()
        self._level = 0
        if self._running != None:
            self._running.cancel()
        self._running = None

    async def test(self, duration=0.1):
        if self.__status__ < ZONE_STATUS_INITIAL:
            self._events.publish(
                ACTIONS.LOG_ERROR, "ZONE TEST ABORTED, invalid zone status")
            return

        self.clear()
        self._turn_on()
        self._events.publish(ACTIONS.HEATER_TESTING, self.name)
        await asyncio.sleep(duration)
        self._turn_off()

    def update_charge(self, timestamp: int) -> float:
        q = 1 - self._res_charge if self.is_live else self._res_charge
        dt = timestamp - self._state_change_timestamp
        adj = 0 if q == 0 else \
            -1 * ((self._C * math.log(q, 10)) /
                  (-self._B * math.log(q, 10) + self._A))
        x = dt + adj
        exponent = (x * self._A) / (self._C + self._B * x)
        dq = 1 - pow(10, -exponent)

        if self.is_live:
            # Charging
            self._charge = dq
        else:
            # Discharging
            self._charge = 1 - dq

        return self._charge

    def adjust_charge_curve(self, vals: dict) -> None:
        if vals['A']:
            self._A = vals['A']
        if vals['B']:
            self._B = vals['B']
        if vals['C']:
            self._C = vals['C']

    def get_curve_settings(self) -> dict:
        return {
            'A': self._A,
            'B': self._B,
            'C': self._C,
        }
