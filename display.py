import uasyncio as asyncio
from pimoroni import Button
from picographics import PicoGraphics, DISPLAY_PICO_DISPLAY_2, PEN_P4

display = PicoGraphics(display=DISPLAY_PICO_DISPLAY_2,
                       pen_type=PEN_P4, rotate=0)
display.set_backlight(0.5)
display.set_font("bitmap8")

button_a = Button(12)
button_b = Button(13)
button_x = Button(14)
button_y = Button(15)

WHITE = display.create_pen(255, 255, 255)
BLACK = display.create_pen(0, 0, 0)
CYAN = display.create_pen(0, 255, 255)
MAGENTA = display.create_pen(255, 0, 255)
YELLOW = display.create_pen(255, 255, 0)
GREEN = display.create_pen(0, 255, 0)


def clear():
    display.set_pen(BLACK)
    display.clear()
    display.update()


async def display_message_async(message: str, duration: int):
    print(message)
    time = 0

    while time < duration:
        clear()
        display.set_pen(GREEN)
        display.text(message, 10, 10, 240, 4)
        display.update()
        await asyncio.sleep(1)
        time += 1


def display_message(message: str):
    print(message)

    clear()
    display.set_pen(GREEN)
    display.text(message, 10, 10, 240, 4)
    display.update()
