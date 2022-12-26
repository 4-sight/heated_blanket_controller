class Actions:
    WIFI_CONNECTING: str
    WIFI_CONNECTED: str
    WIFI_CONNECTION_FAILED: str
    WIFI_CONNECTION_LOST: str

    CLIENT_CONNECTED: str
    CLIENT_DISCONNECTED: str

    SET_ONBOARD_LED: str
    SET_HEATER: str
    APPLY_PRESET: str

    BUTTON_PRESSED: str

    def __init__(self) -> None:
        self.WIFI_CONNECTING = "wifi_connecting"
        self.WIFI_CONNECTED = "wifi_connected"
        self.WIFI_CONNECTION_FAILED = "wifi_connection_failed"
        self.WIFI_CONNECTION_LOST = "wifi_connection_lost"

        self.CLIENT_CONNECTED = "client_connected"
        self.CLIENT_DISCONNECTED = "client_disconnected"

        self.SET_ONBOARD_LED = "set_onboard_led"
        self.SET_HEATER = "set_heater"
        self.APPLY_PRESET = "apply_preset"

        self.BUTTON_PRESSED = "button_pressed"


ACTIONS = Actions()
