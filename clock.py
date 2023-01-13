from machine import RTC
import ntptime
from events import Events, ACTIONS


class Clock:
    _rtc: RTC
    _events: Events

    def __init__(self, events: Events) -> None:
        self._events = events
        self._rtc = RTC()

        events.subscribe(ACTIONS.WIFI_CONNECTED, self.synchronise)

    def synchronise(self, _payload) -> None:
        self._events.publish(ACTIONS.LOG_VERBOSE,
                             "synchronising onboard clock")
        ntptime.settime()
