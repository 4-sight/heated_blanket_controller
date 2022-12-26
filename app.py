from display import Display
from clock import Clock
from logger import Logger
from connection import Connection
from server import Server
from inputs import Inputs
import uasyncio as asyncio
from actions import ACTIONS


class App:
    _display: Display
    _clock: Clock
    _logger: Logger
    _connection: Connection
    _server: Server
    _screen: str

    def __init__(self) -> None:
        self._display = Display()
        self._clock = Clock()
        self._events = dict()
        self._logger = Logger()
        self._inputs = Inputs(self.publish, self._logger)
        self._connection = Connection(self.publish, self._logger)
        self._server = Server(self.publish, self._logger)
        self._screen = "home"

    def subscribe(self, event: str, callback) -> None:
        if event not in self._events.keys():
            self._events[event] = []
        self._events[event].append(callback)

    def publish(self, event: str, payload) -> None:
        self.log('info', "Event: {}\n\t\tPayload: {}".format(event, payload))
        if event in self._events.keys():
            for callback in self._events[event]:
                callback(payload)

    def set_screen(self, screen: str) -> None:
        print("set screen: ", screen)
        self._screen = screen

    def log(self, log_level: str, data: str) -> None:
        self._logger.log(log_level, data)

    def display(self, message: str, log_level: None | str = None) -> None:
        self._display.display_message(message)
        if log_level != None:
            self._logger.log(log_level, message)

    def setup(self) -> None:
        self.display("Beginning setup.")
        self.display("Connecting to Wi-fi...")
        self._connection.connect()
        self.display("Wi-fi connected.")
        self.display("Synchronising clock")
        self._clock.synchronise()
        self.display("Setup finished.")

    async def start(self) -> None:
        asyncio.create_task(self._server.start())
        asyncio.create_task(self._connection.monitor_connection())
        asyncio.create_task(self._inputs.listen())

    async def run(self) -> None:
        self.subscribe(ACTIONS.BUTTON_PRESSED, self.handle_inputs)
        while True:
            self.render()
            await asyncio.sleep(0.1)

    def handle_inputs(self, buttons) -> None:
        if self._screen == "home":
            if buttons['x'].is_pressed:
                self._logger.inc_level()
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
            self.display("Home")

        elif self._screen == "settings":
            self.display("Settings")

        elif self._screen == "control":
            self.display("Control")
