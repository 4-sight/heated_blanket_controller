# import uasyncio as asyncio
# from events import Events, ACTIONS
# from pimoroni import Button


# class Inputs:
#     _events: Events

#     def __init__(self, events: Events) -> None:
#         self._events = events
#         self.buttons = {
#             'a': Button(12, repeat_time=500, hold_time=2000),
#             'b': Button(13, repeat_time=500, hold_time=2000),
#             'x': Button(14, repeat_time=500, hold_time=2000),
#             'y': Button(15, repeat_time=500, hold_time=2000)
#         }

#     async def listen(self) -> None:
#         self._events.publish(ACTIONS.LOG_DEBUG, 'listening for inputs...')

#         while True:
#             for button in self.buttons.values():
#                 if button.read():
#                     self._events.publish(ACTIONS.BUTTON_PRESSED,
#                                          payload=self.buttons,
#                                          log_level=ACTIONS.LOG_INFO)

#             await asyncio.sleep(0.1)
