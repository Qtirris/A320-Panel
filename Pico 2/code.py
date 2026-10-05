import usb_hid

import btn_matriz as mat
from hid_panel import Panel

mat.iniciar_matriz()
mat.describir()          # muestra qué botón es cada función
panel = Panel(usb_hid.devices)

while True:
    mat.escanear_matriz()
    mat.escanear_comandos()
    panel.switch_update(mat.cmd)