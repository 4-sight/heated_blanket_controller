from events import Events, ACTIONS
from channel import Channel
import uasyncio as asyncio


class Control:
    channel_1: Channel
    channel_2: Channel
    _events: Events

    def __init__(self, events: Events) -> None:
        self._events = events
        self.channel_1 = Channel(1, 1, 2, 26, events)
        self.channel_2 = Channel(2, 3, 4, 27, events)

        self._events.subscribe(ACTIONS.APPLY_PRESET, self._handle_presets)

    def _handle_presets(self, preset: int) -> None:
        if preset == 1:
            self._events.publish(ACTIONS.LOG_VERBOSE, "activate preset 1")
            self.channel_1.set_levels(9, 5)
            self.channel_2.set_levels(0, 0)
        elif preset == 2:
            self._events.publish(ACTIONS.LOG_VERBOSE, "activate preset 2")
            self.channel_1.set_levels(9, 0)
            self.channel_2.set_levels(9, 0)
        elif preset == 3:
            self._events.publish(ACTIONS.LOG_VERBOSE, "activate preset 3")
            self.channel_1.set_levels(9, 9)
            self.channel_2.set_levels(9, 9)
        elif preset == 4:
            self._events.publish(ACTIONS.LOG_VERBOSE, "activate preset 4")
            self.channel_1.set_levels(5, 5)
            self.channel_2.set_levels(5, 5)
        elif preset == 5:
            self._events.publish(ACTIONS.LOG_VERBOSE, "activate preset 5")
            self.channel_1.set_levels(1, 1)
            self.channel_2.set_levels(1, 1)
        elif preset == 6:
            self._events.publish(ACTIONS.LOG_VERBOSE, "activate preset 6")
            self.channel_1.set_levels(9, 5)
            self.channel_2.set_levels(9, 5)

    async def test_channels(self) -> None:
        asyncio.create_task(self.channel_1.start_test())
        asyncio.create_task(self.channel_2.start_test())

    async def debug_channels(self) -> None:
        while True:
            safety_val_1 = self.channel_1.get_safety_mv(1)
            safety_val_2 = self.channel_2.get_safety_mv(1)

            self._events.publish(ACTIONS.DISPLAY_MESSAGE,
                                 "'safety_1': {}\n'safety_2': {}".format(safety_val_1, safety_val_2))

            await asyncio.sleep(0.1)

    def take_channel_logs(self) -> dict:
        return {
            'channel_1': self.channel_1.take_safety_logs(),
            'channel_2': self.channel_2.take_safety_logs(),
        }

    def get_curve_data(self, channel_index: int) -> dict:
        if channel_index == 1:
            return self.channel_1.get_curve_data()
        else:
            return self.channel_2.get_curve_data()
