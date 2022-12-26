from machine import Pin
import uasyncio as asyncio
from uasyncio import Task
from events import Events, ACTIONS


class Heater:
    _events: Events
    _level: int
    _name: str
    _output: Pin
    _running: Task | None = None

    def __init__(self, name: str, output: Pin, events: Events) -> None:
        self._events = events
        self._level = 0
        self._name = name
        self._output = output

    def set_level(self, level: int) -> None:
        self._level = level

        if self._running != None:
            self._running.cancel()

        async def run():
            if self._level > 0:
                while True:
                    level = self._level
                    self._events.publish(ACTIONS.LOG_INFO, self._name + " on")
                    self._output.value(1)
                    await asyncio.sleep(level)

                    if level < 10:
                        self._events.publish(
                            ACTIONS.LOG_INFO, self._name + " off")
                        self._output.value(0)
                        await asyncio.sleep(10 - level)

        self._running = asyncio.create_task(run())

    def turn_off(self) -> None:
        self._level = 0
        self._running.cancel()
        self._running = None
