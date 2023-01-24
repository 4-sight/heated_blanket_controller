from events import Events, ACTIONS
from heater import ZONE_STATUS_ERROR_SAFETY_HIGH, ZONE_STATUS_ERROR_SAFETY_LOW, ZONE_STATUS_ERROR_CHANNEL_ERROR, ZONE_STATUS_OK, Heater
from machine import Pin, ADC
import uasyncio as asyncio
from uasyncio import Task
import time
import gc

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
    _safety_logs: list[dict]
    _out_of_range_count: int
    _min_t: int
    _max_t: int
    _mean_t: int
    _mean_count: int
    _RANGE = range(-10, 80)
    _FEET_MAX = 140
    _BODY_MAX = 130

    def __init__(self, index: int, feet_pin: int, body_pin: int, safety_pin: int,  events: Events) -> None:
        self._events = events
        self.index = index
        self.feet = Heater("feet_{}".format(
            index), Pin(feet_pin, Pin.OUT), events, A=0.36, B=0.01, C=210)
        self.body = Heater("body_{}".format(
            index), Pin(body_pin, Pin.OUT), events, A=0.36, B=0.01, C=210)
        self.safety = ADC(safety_pin)
        self._safety_range = MIN_RANGE
        self.__status__ = CHANNEL_STATUS_INITIAL
        self._monitoring = None
        self._safety_logs = []
        self._out_of_range_count = 0
        self._min_t = 10000
        self._max_t = 0
        self._mean_t = 0
        self._mean_count = 0
        self._RANGE = range(-10, 80)
        self._FEET_MAX = 140
        self._BODY_MAX = 130

        events.subscribe(ACTIONS.CHANNEL_SAFETY_DETECTED,
                         self._test_heating_zones)
        events.subscribe(ACTIONS.HEATING_CHANNEL_OUT_OF_RANGE_ERROR,
                         self.on_error)
        events.subscribe(ACTIONS.ADJUST_SAFETY_RANGE, self.adjust_safety_range)
        events.subscribe(ACTIONS.SET_LEVELS, self.set_levels)

    def set_levels(self, levels: dict) -> None:

        if self.__status__ < CHANNEL_STATUS_OK:
            return

        f = levels['f'] if 'f' in levels else self.feet.get_level()
        b = levels['b'] if 'b' in levels else self.body.get_level()

        try:
            if f + b == 0:
                self.turn_off()
                return

            if 'f' in levels:
                self.feet.set_level(f)
            if 'b' in levels:
                self.body.set_level(b)
            self.monitor_safety_val()
        except ValueError:
            self._events.publish(
                ACTIONS.LOG_ERROR, "Attempt to set invalid heating level f:{} b:{}".format(f, b))

    def get_safety_mv(self, sample_size=5) -> int:
        avg_volts = 0

        for i in range(sample_size):
            avg_volts += ((self.safety.read_u16() *
                          CONVERSION_FACTOR) - avg_volts) / (i + 1)

        mv = round(avg_volts * 1000)
        return mv

    async def _detect_safety_output(self) -> None:
        self.feet.clear()
        self.body.clear()
        await asyncio.sleep(0.5)

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
            asyncio.create_task(zone.test(test_duration))
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
                zone.clear()
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

    def _log_safety_data(self, data: dict) -> None:
        self._safety_logs.append(data)

    def _clear_logs(self) -> None:
        for log in self._safety_logs:
            del log

        gc.collect()

        self._safety_logs = []

    def take_safety_logs(self) -> dict:
        safety_logs = self._safety_logs
        self._clear_logs()

        return {
            'logs': safety_logs,
            'exception_count': self._out_of_range_count,
            'min_t': self._min_t,
            'max_t': self._max_t,
            'mean_t': self._mean_t,
            'count': self._mean_count
        }

    def get_curve_data(self) -> dict:
        return {
            'lower': self._RANGE.start,
            'upper': self._RANGE.stop,
            'feet_max': self._FEET_MAX,
            'body_max': self._BODY_MAX,
            'feet_curve': self.feet.get_curve_settings(),
            'body_curve': self.body.get_curve_settings()
        }

    async def _monitor(self):

        while True:

            t = time.ticks_ms()
            fq = self.feet.update_charge(t)
            bq = self.body.update_charge(t)
            safety_val = self.get_safety_mv(1)

            v = int(fq * self._FEET_MAX + bq * self._BODY_MAX)
            predicted_range = range(
                self._RANGE.start + v, self._RANGE.stop + v)

            threshold = min(safety_val - predicted_range.start,
                            predicted_range.stop - safety_val)
            self._min_t = min(self._min_t, threshold)
            self._max_t = max(self._max_t, threshold)
            self._mean_count += 1
            self._mean_t += int((threshold - self._mean_t) / self._mean_count)

            if safety_val not in predicted_range:
                self._out_of_range_count += 1

            # print("SV: {}\tRANGE: {}-{}\tFQ: {}\tBQ: {}\tF:{}B:{}".format(safety_val,
            #       predicted_range.start, predicted_range.stop, fq, bq, self.feet.is_live, self.body.is_live))

            self._log_safety_data({
                't': t,
                'sv': safety_val,
                'r_start': predicted_range.start,
                'r_stop': predicted_range.stop,
                'fq': fq,
                'bq': bq,
                'f': self.feet.is_live,
                'b': self.body.is_live
            })

            # Manual garbage collection
            del t
            del fq
            del bq
            del safety_val
            del v
            del predicted_range
            del threshold
            gc.collect()

            await asyncio.sleep(0.05)

    def monitor_safety_val(self) -> None:
        if self._monitoring == None:
            self._monitoring = asyncio.create_task(self._monitor())

    def restart_monitoring(self) -> None:
        if self._monitoring:
            self._monitoring.cancel()
            self._monitoring = None
            self._safety_logs = []
            self._out_of_range_count = 0
            self._min_t = 10000
            self._max_t = 0
            self._mean_t = 0
            self._mean_count = 0

        self.monitor_safety_val()

    def adjust_safety_range(self, vals: dict) -> None:
        self.restart_monitoring()

        if vals['channel'] != self.index:
            return

        if vals['lower']:
            self._RANGE = range(vals['lower'], self._RANGE.stop)
        if vals['upper']:
            self._RANGE = range(self._RANGE.start, vals['upper'])
        if vals['feet_max']:
            self._FEET_MAX = vals['feet_max']
        if vals['body_max']:
            self._BODY_MAX = vals['body_max']

        if vals['feet_curve']:
            self.feet.adjust_charge_curve(vals['feet_curve'])
        if vals['body_curve']:
            self.body.adjust_charge_curve(vals['body_curve'])

    def get_status(self):
        return {
            'index': self.index,
            'channel_status': self.__status__,
            'feet_status': self.feet.get_status(),
            'body_status': self.body.get_status()
        }

    def get_zone_levels(self) -> dict:
        return {
            'f': self.feet.get_level(),
            'b': self.body.get_level()
        }

    def turn_off(self):
        self.feet.clear()
        self.body.clear()

    def on_error(self, payload):
        if payload['channel'] == self.index:
            self.turn_off()
            self.__status__ = CHANNEL_STATUS_ERROR
            self.feet.set_status(ZONE_STATUS_ERROR_CHANNEL_ERROR)
            self.body.set_status(ZONE_STATUS_ERROR_CHANNEL_ERROR)
