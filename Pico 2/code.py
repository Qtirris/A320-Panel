import time
import usb_hid

import btn_matriz as mat
from hid_panel import Panel

panel=Panel(usb_hid.devices)

import board
import digitalio
import usb_hid
from adafruit_hid import find_device

mat.iniciar_matriz()

panel = Panel(usb_hid.devices)
while True:
    mat.escanear_matriz()
    mat.escanear_comandos()
    panel.switch_update(mat.matriz_cmd)
