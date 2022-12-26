from clock import Clock

LEVELS = {
    'debug': 0,
    'info': 1,
    'log': 2,
    'warn': 1,
    'error': 2
}


class Logger:
    _clock: Clock
    _level: int

    def __init__(self, clock: Clock) -> None:
        self.clock = clock
        self._level = 2

    def set_level(self, level: int) -> None:
        self._level = level

    def inc_level(self) -> None:
        new_level = (self._level + 1) % 3
        print("Logging level: ", new_level)
        self.set_level(new_level)

    def log(self, log_level: str, data: str) -> None:
        level = LEVELS[log_level]

        if level >= self._level:
            print("{}:\t\t{}".format(log_level.upper(), data))
