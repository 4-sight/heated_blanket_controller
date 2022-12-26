class Events:

    def __init__(self) -> None:
        self._events = dict()

    def subscribe(self, event: str, callback) -> None:
        if event not in self._events.keys():
            self._events[event] = []
        self._events[event].append(callback)

    def publish(self, event: str, payload) -> None:
        for callback in self._events[ACTIONS.LOG_VERBOSE]:
            callback(
                "Event: {}\n\t\tPayload: {}".format(event, payload))
        if event in self._events.keys():
            for callback in self._events[event]:
                callback(payload)


class ACTIONS:
    LOG_DEBUG: str = "log_debug"
    LOG_VERBOSE: str = "log_verbose"
    LOG_INFO: str = "log_info"
    LOG_WARN: str = "log_warn"
    LOG_ERROR: str = "log_error"
    LOG_LEVEL_SET: str = "set_logging_level"
    LOG_LEVEL_INC: str = "increment_logging_level"
    LOGGING_MUTE: str = "mute_logging"

    WIFI_CONNECTING: str = "wifi_connecting"
    WIFI_CONNECTED: str = "wifi_connected"
    WIFI_CONNECTION_FAILED: str = "wifi_connection_failed"
    WIFI_CONNECTION_LOST: str = "wifi_connection_lost"

    CLIENT_CONNECTED: str = "client_connected"
    CLIENT_DISCONNECTED: str = "client_disconnected"

    SET_ONBOARD_LED: str = "set_onboard_led"
    SET_HEATER: str = "set_heater"
    APPLY_PRESET: str = "apply_preset"

    BUTTON_PRESSED: str = "button_pressed"

    DISPLAY_MESSAGE: str = "display_message"
