import time

import btn_matriz as mat

import board
import digitalio
import usb_hid
from adafruit_hid import find_device

mat.iniciar_matriz()

while True:
    mat.escanear_matriz()
