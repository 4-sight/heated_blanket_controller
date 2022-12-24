import uasyncio as asyncio
from pimoroni import Button
from picographics import PicoGraphics, DISPLAY_PICO_DISPLAY_2, PEN_P4


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
    _prev_message: str

    def __init__(self) -> None:
        self._display = PicoGraphics(display=DISPLAY_PICO_DISPLAY_2,
                                     pen_type=PEN_P4, rotate=0)
        self._display.set_backlight(0.5)
        self._display.set_font("bitmap8")
        self._pens = Pens(self._display)
        self._prev_message = ""
        self.display_message("display setup")

    def clear(self):
        display = self._display
        display.set_pen(self._pens.BLACK)
        display.clear()
        display.update()

    def display_message(self, message: str) -> None:
        display = self._display

        if message != self._prev_message:
            self.clear()
            display.set_pen(self._pens.GREEN)
            display.text(message, 10, 10, 240, 4)
            self._prev_message = message
            display.update()

    async def display_message_async(self, message: str, duration: int):
        print(message)
        display = self._display
        time = 0

        while time < duration:
            self.clear()
            display.set_pen(self._pens.GREEN)
            display.text(message, 10, 10, 240, 4)
            display.update()
            await asyncio.sleep(1)
            time += 1
