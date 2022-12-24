from machine import RTC
import ntptime
import time


class Clock:
    _rtc: RTC

    def __init__(self) -> None:
        self._rtc = RTC()

    def synchronise(self) -> None:
        ntptime.settime()

    def get_timestamp(self) -> int:
        return time.time()
