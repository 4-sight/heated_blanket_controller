from events import Events, ACTIONS

LEVELS = {
    'debug': 0,
    'verbose': 1,
    'info': 2,
    'warn': 1,
    'error': 2
}


class Logger:
    _level: int
    _events: Events

    def __init__(self, events: Events) -> None:
        self._level = 1
        self._events = events

        self._events.subscribe(ACTIONS.LOG_DEBUG, self._log_debug)
        self._events.subscribe(ACTIONS.LOG_VERBOSE, self._log_verbose)
        self._events.subscribe(ACTIONS.LOG_INFO, self._log_info)
        self._events.subscribe(ACTIONS.LOG_WARN, self._log_warn)
        self._events.subscribe(ACTIONS.LOG_ERROR, self._log_error)
        self._events.subscribe(ACTIONS.LOG_LEVEL_SET, self._set_level)
        self._events.subscribe(ACTIONS.LOG_LEVEL_INC, self._inc_level)
        self._events.subscribe(ACTIONS.LOGGING_MUTE, self._mute_logging)

    def _set_level(self, level: int) -> None:
        try:
            self._level = int(level) % 3
        except ValueError:
            self._events.publish(
                ACTIONS.LOG_ERROR, "Unable to set logging level, invalid level: {}".format(level))

    def get_level(self) -> int:
        return self._level

    def _inc_level(self, _payload) -> None:
        new_level = (self._level + 1) % 3
        self._log('info', "Logging level: {}".format(new_level))
        self._set_level(new_level)

    def _mute_logging(self, _payload) -> None:
        self._log('info', "Logging muted.")
        self._set_level(3)

    def _log(self, log_level: str, data: str) -> None:
        level = LEVELS[log_level]

        if level >= self._level:
            print("{}:\t\t{}".format(log_level.upper(), data))

    def _log_debug(self, data: str) -> None:
        self._log("debug", data)

    def _log_verbose(self, data: str) -> None:
        self._log("verbose", data)

    def _log_info(self, data: str) -> None:
        self._log("info", data)

    def _log_warn(self, data: str) -> None:
        self._log("warn", data)

    def _log_error(self, data: str) -> None:
        self._log("error", data)
