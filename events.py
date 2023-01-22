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
    SET_LEVELS: str = "set_channel_levels"

    BUTTON_PRESSED: str = "button_pressed"
    SAFETY_OUTPUT_READ: str = "safety_output_read"

    DISPLAY_SET_SCREEN: str = "set_display_screen"
    DISPLAY_ALERT: str = "display_alert"
    DISPLAY_MESSAGE: str = "display_message"

    CHANNEL_SAFETY_NOT_PRESENT: str = "channel_safety_not_present"
    CHANNEL_SAFETY_DETECTED: str = "channel_safety_detected"

    HEATER_TESTING: str = "heater_testing"
    HEATING_ZONE_OUT_OF_RANGE_ERROR: str = "Error: heating zone out of range"
    HEATING_ZONE_IN_RANGE: str = "Heating zone in range"
    HEATING_CHANNEL_OUT_OF_RANGE_ERROR: str = "Error: heating channel out of range"
    HEATING_CHANNEL_TEST_PASSED: str = "heating channel test passed"

    ADJUST_SAFETY_RANGE: str = "adjust safety range"


class Events:
    _events: dict[str, list]

    def __init__(self) -> None:
        self._events = dict()

    def subscribe(self, event: str, callback) -> None:
        if event not in self._events.keys():
            self._events[event] = []
        self._events[event].append(callback)

    def publish(self, event: str, payload, log_level=ACTIONS.LOG_DEBUG) -> None:
        for callback in self._events[log_level]:
            callback(
                "Event: {}\n\t\tPayload: {}".format(event, payload))
        if event in self._events.keys():
            for callback in self._events[event]:
                callback(payload)
