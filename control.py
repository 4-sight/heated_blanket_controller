from events import Events, ACTIONS
from heater import Heater
from machine import Pin


class Control:
    _events: Events
    _feet_1: Heater
    _body_1: Heater
    _feet_2: Heater
    _body_2: Heater

    def __init__(self, events: Events) -> None:
        self._events = events
        self._feet_1 = Heater("feet_1", Pin(1, Pin.OUT), events)
        self._body_1 = Heater("body_1", Pin(2, Pin.OUT), events)
        self._feet_2 = Heater("feet_2", Pin(3, Pin.OUT), events)
        self._body_2 = Heater("body_2", Pin(4, Pin.OUT), events)

        self._events.subscribe(ACTIONS.APPLY_PRESET, self._handle_presets)

    def _handle_presets(self, preset: int) -> None:
        if preset == 1:
            self._events.publish(ACTIONS.LOG_VERBOSE, "activate preset 1")
            self._feet_1.set_level(9)
            self._body_1.set_level(5)

            self._feet_2.set_level(0)
            self._body_2.set_level(0)
        elif preset == 2:
            self._events.publish(ACTIONS.LOG_VERBOSE, "activate preset 2")
            self._feet_1.set_level(9)
            self._body_1.set_level(0)

            self._feet_2.set_level(9)
            self._body_2.set_level(0)
        elif preset == 3:
            self._events.publish(ACTIONS.LOG_VERBOSE, "activate preset 3")
            self._feet_1.set_level(9)
            self._body_1.set_level(9)

            self._feet_2.set_level(9)
            self._body_2.set_level(9)
        elif preset == 4:
            self._events.publish(ACTIONS.LOG_VERBOSE, "activate preset 4")
            self._feet_1.set_level(5)
            self._body_1.set_level(5)

            self._feet_2.set_level(5)
            self._body_2.set_level(5)
        elif preset == 5:
            self._events.publish(ACTIONS.LOG_VERBOSE, "activate preset 5")
            self._feet_1.set_level(1)
            self._body_1.set_level(1)

            self._feet_2.set_level(1)
            self._body_2.set_level(1)
        elif preset == 6:
            self._events.publish(ACTIONS.LOG_VERBOSE, "activate preset 6")
            self._feet_1.set_level(9)
            self._body_1.set_level(5)

            self._feet_2.set_level(9)
            self._body_2.set_level(5)
