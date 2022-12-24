# from app import App
# import uasyncio as asyncio
# from uasyncio import Task
# from actions import ACTIONS
# from machine import Pin


# class Pulse:
#     _rate: int = 0
#     _duration: int = 0
#     _task: Task | None = None
#     _led: Pin

#     def __init__(self, pin: Pin) -> None:
#         self._led = pin

#     def set_rate(self, rate: int) -> None:
#         self._rate = rate

#     def set_duration(self, duration: int) -> None:
#         self._duration = duration

#     def get_rate(self) -> int:
#         return self._rate

#     def get_duration(self) -> int:
#         return self._duration

#     def start(self):
#         async def inner():
#             rate = self._rate
#             while self._duration > 0:
#                 if rate > 0:
#                     print("led on")
#                     self._led.value(1)
#                     await asyncio.sleep(rate)

#                 if rate < 10:
#                     print("led off")
#                     self._led.value(0)
#                     await asyncio.sleep(10 - rate)

#                 self._duration -= 10

#         self._task = asyncio.create_task(inner())

#     def stop(self):
#         if self._task != None:
#             self._task.cancel()

#     def clear(self):
#         self._led.value(0)
#         self.set_rate(0)
#         self.set_duration(0)


# class Control:
#     _app: App
#     _onboard: Pin
#     _pulse: Pulse

#     def __init__(self, store: App) -> None:
#         self._app = store
#         self._onboard = Pin('LED', Pin.OUT)
#         self._pulse = Pulse(Pin(1, Pin.OUT))

#         store.subscribe(ACTIONS.SET_ONBOARD_LED, self.on_onboard_change)

#     def on_onboard_change(self, payload) -> None:
#         if "turn_on" not in payload:
#             return

#         turn_on = payload['turn_on']
#         if turn_on:
#             self._onboard.value(1)
#             self._app.display("onboard led on", 'info')
#         else:
#             self._onboard.value(0)
#             self._app.display("onboard led off", 'info')

#     def on_pulse_led_change(self, payload) -> None:
#         if "pulse" not in payload:
#             return

#         self._pulse.stop()
#         rate = payload['pulse']['rate']
#         if rate != None:
#             rate = int(rate)
#             self._pulse.set_rate(rate)
#             self._pulse.set_duration(60)
#             self._pulse.start()

#     def on_pulse_stop(self) -> None:
#         self._pulse.clear()
#         self._pulse.stop()
