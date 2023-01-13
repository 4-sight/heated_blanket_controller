from events import Events, ACTIONS
from heater import ZONE_STATUS_ERROR_SAFETY_HIGH, ZONE_STATUS_ERROR_SAFETY_LOW, ZONE_STATUS_ERROR_CHANNEL_ERROR, ZONE_STATUS_OK, Heater
from machine import Pin, ADC
import uasyncio as asyncio
from uasyncio import Task

CONVERSION_FACTOR = 3.3 / 65535
MIN_RANGE = range(0, 60)
FEET_ONLY_RANGE = range(100, 200)
BODY_ONLY_RANGE = range(100, 200)
DUAL_ZONE_RANGE = range(100, 350)
MAX_RETRY_INTERVAL = 100

CHANNEL_STATUS_INITIAL = 0
CHANNEL_STATUS_NOT_CONNECTED = 1
CHANNEL_STATUS_CONNECTED = 2
CHANNEL_STATUS_OK = 3
CHANNEL_STATUS_ERROR = -1


class Channel:
    feet: Heater
    body: Heater
    safety: ADC
    index: int
    _monitoring: Task | None
    _events: Events
    _safety_range: range
    __status__: int

    def __init__(self, index: int, feet_pin: int, body_pin: int, safety_pin: int,  events: Events) -> None:
        self._events = events
        self.index = index
        self.feet = Heater("feet_{}".format(
            index), Pin(feet_pin, Pin.OUT), events)
        self.body = Heater("body_{}".format(
            index), Pin(body_pin, Pin.OUT), events)
        self.safety = ADC(safety_pin)
        self._safety_range = MIN_RANGE
        self.__status__ = CHANNEL_STATUS_INITIAL
        self._monitoring = None

        events.subscribe(ACTIONS.CHANNEL_SAFETY_DETECTED,
                         self._test_heating_zones)
        events.subscribe(ACTIONS.HEATING_CHANNEL_OUT_OF_RANGE_ERROR,
                         self.on_error)

    def set_levels(self, feet_level: int, body_level: int) -> None:
        if self.__status__ >= CHANNEL_STATUS_OK:

            if feet_level + body_level == 0:
                self.turn_off()
            else:
                self.feet.set_level(feet_level)
                self.body.set_level(body_level)
                self.monitor_safety_val()

    def get_safety_mv(self, sample_size=5) -> int:
        avg_volts = 0

        for i in range(sample_size):
            avg_volts += ((self.safety.read_u16() *
                          CONVERSION_FACTOR) - avg_volts) / (i + 1)

        mv = round(avg_volts * 1000)
        return mv

    async def _detect_safety_output(self) -> None:
        init_safety_val = self.get_safety_mv()
        retry_interval = 1
        attempt = 0

        while init_safety_val not in self._safety_range:
            attempt = (attempt + 1) % 10

            self._events.publish(
                ACTIONS.CHANNEL_SAFETY_NOT_PRESENT,
                "channel: {} safety val: {}".format(
                    self.index, init_safety_val),
                log_level=ACTIONS.LOG_WARN)

            await asyncio.sleep(retry_interval)

            if attempt == 0:
                retry_interval = min(retry_interval * 10, MAX_RETRY_INTERVAL)

            init_safety_val = self.get_safety_mv()

        self._events.publish(ACTIONS.CHANNEL_SAFETY_DETECTED,
                             payload={'channel': self.index},
                             log_level=ACTIONS.LOG_INFO)
        self.__status__ = CHANNEL_STATUS_CONNECTED

    async def _test_zones(self, zones: list[Heater]) -> None:
        if self.__status__ < CHANNEL_STATUS_CONNECTED:
            self._events.publish(
                ACTIONS.LOG_ERROR, "ZONE TEST ABORTED, invalid channel status")
            return

        tested_zones: list[str] = []
        test_duration = 0.2
        for zone in zones:
            tested_zones.append(zone.name)
            asyncio.create_task(zone.energise(test_duration))
        await asyncio.sleep(test_duration - 0.1)
        safety_val = self.get_safety_mv()

        payload = {
            'zones': tested_zones,
            'safety value': safety_val
        }

        if safety_val not in self._safety_range:
            self.__status__ = CHANNEL_STATUS_ERROR
            if safety_val < self._safety_range.start:
                zone_status = ZONE_STATUS_ERROR_SAFETY_LOW
            else:
                zone_status = ZONE_STATUS_ERROR_SAFETY_HIGH

            for zone in zones:
                zone.turn_off()
                zone.set_status(zone_status)

            self._events.publish(
                ACTIONS.HEATING_ZONE_OUT_OF_RANGE_ERROR, payload, log_level=ACTIONS.LOG_ERROR)
        else:
            for zone in zones:
                zone.set_status(ZONE_STATUS_OK)

            self._events.publish(ACTIONS.HEATING_ZONE_IN_RANGE,
                                 payload, log_level=ACTIONS.LOG_INFO)

    async def start_test(self) -> None:
        if self.__status__ < CHANNEL_STATUS_INITIAL:
            self._events.publish(
                ACTIONS.LOG_ERROR, "TEST ABORTED, invalid channel status")
            return

        self.__status__ = 1
        self.feet.turn_off()
        self.body.turn_off()
        await asyncio.sleep(0.5)
        asyncio.create_task(self._detect_safety_output())

    def _test_heating_zones(self, payload) -> None:

        async def _test():
            # test feet heating zone
            self._safety_range = FEET_ONLY_RANGE
            await self._test_zones([self.feet])

            # test body heating zone
            self._safety_range = BODY_ONLY_RANGE
            await self._test_zones([self.body])

            # test dual zones
            self._safety_range = DUAL_ZONE_RANGE
            await self._test_zones([self.feet, self.body])

            if self.__status__ >= 2:
                self._events.publish(ACTIONS.HEATING_CHANNEL_TEST_PASSED,
                                     "channel: {}".format(self.index), log_level=ACTIONS.LOG_INFO)
                self.__status__ = CHANNEL_STATUS_OK

        if payload['channel'] == self.index:
            asyncio.create_task(_test())

    def monitor_safety_val(self) -> None:
        if self._monitoring == None:

            async def _monitor():
                while True:
                    self.update_safety_range()
                    safety_val = self.get_safety_mv(1)

                    if safety_val not in self._safety_range:

                        self._events.publish(ACTIONS.HEATING_CHANNEL_OUT_OF_RANGE_ERROR,
                                             payload={'channel': self.index, 'safety_val': safety_val}, log_level=ACTIONS.LOG_ERROR)

                    await asyncio.sleep(0.01)

            self._monitoring = asyncio.create_task(_monitor())

    def get_status(self):
        return {
            'index': self.index,
            'channel_status': self.__status__,
            'feet_status': self.feet.get_status(),
            'body_status': self.body.get_status()
        }

    def turn_off(self):
        self.feet.turn_off()
        self.body.turn_off()

    def on_error(self):
        self.turn_off()
        self.__status__ = CHANNEL_STATUS_ERROR
        self.feet.set_status(ZONE_STATUS_ERROR_CHANNEL_ERROR)
        self.body.set_status(ZONE_STATUS_ERROR_CHANNEL_ERROR)

    def update_safety_range(self):
        feet_live = self.feet.is_live
        body_live = self.body.is_live

        if feet_live & body_live:
            self._safety_range = DUAL_ZONE_RANGE
        elif feet_live:
            self._safety_range = FEET_ONLY_RANGE
        elif body_live:
            self._safety_range = BODY_ONLY_RANGE
        else:
            self._safety_range = MIN_RANGE
