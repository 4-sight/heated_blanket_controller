from machine import Pin


class Heater:
    _level: int
    _name: str
    _output: Pin

    def __init__(self, name: str, output: Pin) -> None:
        self._level = 0
        self._name = name
        self._output = output
