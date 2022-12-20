import rp2
import network
import machine
import time

from display import display_message


def connect_to_wifi(ssid, password):
    display_message('Connecting to Network...')
    rp2.country('EN')

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)

    timeout = 10
    while timeout > 0:
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        timeout -= 1
        display_message('Waiting for connection...')
        time.sleep(1)

    if wlan.status() != 3:
        raise RuntimeError('Wi-fi connection failed')
    else:
        led = machine.Pin('LED', machine.Pin.OUT)
        for _ in range(wlan.status()):
            led.on()
            time.sleep(.2)
            led.off()
        display_message('Connected')
        status = wlan.ifconfig()
        display_message('ip = ' + status[0])
