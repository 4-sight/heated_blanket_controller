class Actions:
    WIFI_CONNECTING: str
    WIFI_CONNECTED: str
    WIFI_CONNECTION_FAILED: str
    WIFI_CONNECTION_LOST: str
    SET_STATE: str
    CLIENT_CONNECTED: str
    CLIENT_DISCONNECTED: str

    def __init__(self) -> None:
        self.WIFI_CONNECTING = "wifi_connecting"
        self.WIFI_CONNECTED = "wifi_connected"
        self.WIFI_CONNECTION_FAILED = "wifi_connection_failed"
        self.WIFI_CONNECTION_LOST = "wifi_connection_lost"
        self.SET_STATE = "set_state_{}"
        self.CLIENT_CONNECTED = "client_connected"
        self.CLIENT_DISCONNECTED = "client_disconnected"


ACTIONS = Actions()


class PicoStore:

    def __init__(self) -> None:
        self._events = dict()

    def __setitem__(self, __name: str, __value) -> None:
        self[__name] = __value

    def set_state(self, name: str, value) -> None:
        self[name] = value
        self.publish(ACTIONS.SET_STATE.format(name))

    def subscribe(self, event: str, callback) -> None:
        if event not in self._events.keys():
            self._events[event] = []
        self._events[event].append(callback)

    def publish(self, event: str) -> None:
        if event in self._events.keys():
            for callback in self._events[event]:
                callback()
