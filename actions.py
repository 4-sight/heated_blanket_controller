class Actions:
    WIFI_CONNECTING: str
    WIFI_CONNECTED: str
    WIFI_CONNECTION_FAILED: str
    WIFI_CONNECTION_LOST: str
    SET_STATE: str
    CLIENT_CONNECTED: str
    CLIENT_DISCONNECTED: str
    PULSE_STOP: str

    def __init__(self) -> None:
        self.WIFI_CONNECTING = "wifi_connecting"
        self.WIFI_CONNECTED = "wifi_connected"
        self.WIFI_CONNECTION_FAILED = "wifi_connection_failed"
        self.WIFI_CONNECTION_LOST = "wifi_connection_lost"
        self.SET_STATE = "set_state_{}"
        self.CLIENT_CONNECTED = "client_connected"
        self.CLIENT_DISCONNECTED = "client_disconnected"
        self.PULSE_STOP = "pulse_stop"


ACTIONS = Actions()
