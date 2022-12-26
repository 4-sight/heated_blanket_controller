from display import Display
from clock import Clock
from logger import Logger
from connection import Connection
from server import Server
from inputs import Inputs
import uasyncio as asyncio
from events import Events, ACTIONS


class App:
    _events:  Events
    _display: Display
    _clock: Clock
    _logger: Logger
    _connection: Connection
    _server: Server
    _screen: str

    def __init__(self) -> None:
        self._events = Events()
        self._display = Display(self._events)
        self._clock = Clock(self._events)
        self._logger = Logger(self._events)
        self._inputs = Inputs(self._events)
        self._connection = Connection(self._events)
        self._server = Server(self._events)
        self._screen = "home"

    def set_screen(self, screen: str) -> None:
        print("set screen: ", screen)
        self._screen = screen

    def setup(self) -> None:
        self._events.publish(ACTIONS.DISPLAY_MESSAGE, "Beginning setup.")
        self._events.publish(ACTIONS.DISPLAY_MESSAGE, "Connecting to Wi-fi...")
        self._connection.connect()
        self._events.publish(ACTIONS.DISPLAY_MESSAGE, "Wi-fi connected.")
        self._events.publish(ACTIONS.DISPLAY_MESSAGE, "Synchronising clock")
        self._clock.synchronise()
        self._events.publish(ACTIONS.DISPLAY_MESSAGE, "Setup finished.")

    async def start(self) -> None:
        asyncio.create_task(self._server.start())
        asyncio.create_task(self._connection.monitor_connection())
        asyncio.create_task(self._inputs.listen())

    async def run(self) -> None:
        self._events.subscribe(ACTIONS.BUTTON_PRESSED, self.handle_inputs)
        while True:
            self.render()
            await asyncio.sleep(0.1)

    def handle_inputs(self, buttons) -> None:
        if self._screen == "home":
            if buttons['x'].is_pressed:
                self._events.publish(ACTIONS.LOG_LEVEL_INC, None)
            if buttons['y'].is_pressed:
                self.set_screen('home')
            if buttons['a'].is_pressed:
                self.set_screen('settings')
            if buttons['b'].is_pressed:
                self.set_screen('control')
        elif self._screen == "control":
            if buttons['y'].is_pressed:
                self.set_screen('home')
            if buttons['a'].is_pressed:
                self.set_screen('home')
            if buttons['b'].is_pressed:
                self.set_screen('settings')
        elif self._screen == "settings":
            if buttons['y'].is_pressed:
                self.set_screen('home')
            if buttons['a'].is_pressed:
                self.set_screen('control')
            if buttons['b'].is_pressed:
                self.set_screen('home')

    def render(self) -> None:
        if self._screen == "home":
            self._events.publish(ACTIONS.DISPLAY_MESSAGE, "Home")

        elif self._screen == "settings":
            self._events.publish(ACTIONS.DISPLAY_MESSAGE, "Settings")

        elif self._screen == "control":
            self._events.publish(ACTIONS.DISPLAY_MESSAGE, "Control")
