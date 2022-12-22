from actions import ACTIONS
from display import Display


class PicoStore:
    _display: Display

    def __init__(self, display: Display) -> None:
        self._display = display
        self._events = dict()
        self._store = dict()

    def set_state(self, name: str, value) -> None:
        self._store[name] = value
        self.publish(ACTIONS.SET_STATE.format(name))

    def get_state(self, name: str):
        value = self._store.get(name, None)
        return value

    def subscribe(self, event: str, callback) -> None:
        if event not in self._events.keys():
            self._events[event] = []
        self._events[event].append(callback)

    def publish(self, event: str) -> None:
        self._display.display_message("Event: {}".format(event))
        if event in self._events.keys():
            for callback in self._events[event]:
                callback()
