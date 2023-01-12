from picographics import PicoGraphics, DISPLAY_PICO_DISPLAY_2, PEN_P4
from events import Events, ACTIONS
import time
import uasyncio as asyncio
from uasyncio import Task


class Pens:
    _display: PicoGraphics

    def __init__(self, display) -> None:
        self._display = display
        self.WHITE = display.create_pen(255, 255, 255)
        self.BLACK = display.create_pen(0, 0, 0)
        self.CYAN = display.create_pen(0, 255, 255)
        self.MAGENTA = display.create_pen(255, 0, 255)
        self.YELLOW = display.create_pen(255, 255, 0)
        self.GREEN = display.create_pen(0, 255, 0)


class Display:
    _display: PicoGraphics
    _pens: Pens
    _screen: str
    _alerts: list[str]
    _show_alert: int
    _alert_clearer: Task | None

    def __init__(self, events: Events) -> None:
        self._events = events
        self._alerts = []
        self._alert_clearer = None
        self._display = PicoGraphics(display=DISPLAY_PICO_DISPLAY_2,
                                     pen_type=PEN_P4, rotate=0)
        self._display.set_backlight(0.5)
        self._display.set_font("bitmap8")
        self._pens = Pens(self._display)
        self._prev_message = ""
        self._screen = ""
        self._events.subscribe(ACTIONS.DISPLAY_ALERT, self._push_alert)
        self._events.subscribe(ACTIONS.DISPLAY_SET_SCREEN, self._set_screen)
        self._events.subscribe(ACTIONS.SAFETY_OUTPUT_READ,
                               self._render_safety_output)
        self._push_alert("display setup")

    def _clear(self):
        display = self._display
        display.set_pen(self._pens.BLACK)
        display.clear()
        display.update()

    def _push_alert(self, alert: str):
        self._alerts.append(alert)
        asyncio.create_task(self._render_screen())

        if self._alert_clearer != None:
            self._alert_clearer.cancel()

        self._alert_clearer = asyncio.create_task(self._clear_alerts())

    async def _clear_alerts(self) -> None:
        await asyncio.sleep(2)

        self._alerts = []
        self._alert_clearer = None
        await self._render_screen()

    def _display_message(self, message: str) -> None:
        display = self._display

        if message != self._prev_message:
            self._clear()
            display.set_pen(self._pens.GREEN)
            display.text(message, 10, 10, 240, 4)
            self._prev_message = message
            display.update()

    def _set_screen(self, screen: str) -> None:
        if screen != self._screen:
            self._screen = screen
            asyncio.create_task(self._render_screen())

    async def _render_screen(self) -> None:
        if len(self._alerts) > 0:

            alert = '\n'.join(self._alerts)
            self._display_message(alert)

        else:
            if self._screen == "home":
                self._display_message("home")
            elif self._screen == "control":
                self._display_message("control")

            elif self._screen == "settings":
                self._display_message("settings")

    def _render_safety_output(self, readings) -> None:
        if self._screen == "control":
            display = self._display

            self._clear()
            display.set_pen(self._pens.GREEN)
            display.text("control", 10, 10, 240, 4)
            display.set_pen(self._pens.WHITE)
            display.text("safety 1: {}\nsafety 2: {}".format(
                readings['safety_1'], readings['safety_2']), 10, 50, 240, 4)
            display.update()
