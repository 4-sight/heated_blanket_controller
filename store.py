actions = dict(
    wifi_connecting="wifi_connecting",
    wifi_connected="wifi_connected",
    wifi_connection_failed="wifi_connection_failed",
    wifi_connection_lost="wifi_connection_lost",
    set_state="set_state_{}",
)


class PicoStore:

    def __init__(self) -> None:
        self._events = dict()

    # def __setitem__(self, __name: str, __value) -> None:
    #     self[__name] = __value

    # def set_state(self, name: str, value) -> None:
    #     self[name] = value
    #     self.publish(actions['set_state'].format(__name))

    def subscribe(self, event: str, callback) -> None:
        if event not in self._events.keys():
            self._events[event] = []
        self._events[event].append(callback)

    def publish(self, event: str) -> None:
        if event in self._events.keys():
            for callback in self._events[event]:
                callback()
