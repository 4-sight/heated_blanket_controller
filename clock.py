from machine import RTC
import ntptime
from events import Events, ACTIONS


class Clock:
    _rtc: RTC
    _events: Events

    def __init__(self, events: Events) -> None:
        self._events = events
        self._rtc = RTC()

    def synchronise(self) -> None:
        ntptime.settime()
