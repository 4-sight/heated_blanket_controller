from events import Events, ACTIONS
from heater import ZONE_STATUS_ERROR_SAFETY_HIGH, ZONE_STATUS_ERROR_SAFETY_LOW, ZONE_STATUS_OK, Heater
from machine import Pin, ADC
import uasyncio as asyncio

CONVERSION_FACTOR = 3.3 / 65535
MIN_RANGE = range(0, 60)
FEET_ONLY_RANGE = range(125, 175)
BODY_ONLY_RANGE = range(150, 200)
DUAL_ZONE_RANGE = range(150, 350)
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

        events.subscribe(ACTIONS.CHANNEL_SAFETY_DETECTED,
                         self._test_heating_zones)

    def set_levels(self, feet_level: int, body_level: int) -> None:
        if self.__status__ >= CHANNEL_STATUS_OK:
            self.feet.set_level(feet_level)
            self.body.set_level(body_level)

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
                             "channel: {}".format(self.index),
                             log_level=ACTIONS.LOG_INFO)
        self.__status__ = CHANNEL_STATUS_CONNECTED

    async def _test_zones(self, zones: list[Heater]) -> None:
        if self.__status__ < CHANNEL_STATUS_CONNECTED:
            self._events.publish(
                ACTIONS.LOG_ERROR, "ZONE TEST ABORTED, invalid channel status")
            return

        tested_zones: list[str] = []
        test_duration = 2
        for zone in zones:
            tested_zones.append(zone.name)
            asyncio.create_task(zone.energise(test_duration))
        await asyncio.sleep(test_duration - 0.5)
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

    def _test_heating_zones(self, _payload) -> None:

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

            self._events.publish(ACTIONS.HEATING_CHANNEL_TEST_PASSED,
                                 "channel: {}".format(self.index), log_level=ACTIONS.LOG_INFO)
            self.__status__ = CHANNEL_STATUS_OK

        asyncio.create_task(_test())

    async def monitor_safety_val(self) -> None:
        while True:
            safety_val = self.get_safety_mv(1)

            self._events.publish(ACTIONS.SAFETY_OUTPUT_READ,
                                 'CHANNEL_{} SAFETY_VAL: {}'.format(self.index, safety_val))

            await asyncio.sleep(0.01)

    def get_status(self):
        return {
            'index': self.index,
            'channel_status': self.__status__,
            'feet_status': self.feet.get_status(),
            'body_status': self.body.get_status()
        }
