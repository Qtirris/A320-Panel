# Matriz 2x2 -> gamepad HID de 4 botones (Raspberry Pi Pico 2, CircuitPython)
# Versión con PULL-UP (la Pico 2 / RP2350 tiene una errata con los pull-down internos).
#
# Requiere:
#   - boot.py de esta misma carpeta (descriptor de 4 botones)
#   - /lib/adafruit_hid/  (del bundle de Adafruit; NO hace falta hid_gamepad.py)
#
# Cableado:
#   Fila 1 -> GP15, Fila 2 -> GP14, Columna 1 -> GP13, Columna 2 -> GP12

import time

import board
import digitalio
import usb_hid
from adafruit_hid import find_device

# Localiza el gamepad declarado en boot.py (usage_page 0x01, usage 0x05).
gamepad = find_device(usb_hid.devices, usage_page=0x01, usage=0x05)

ROW_PINS = (board.GP15, board.GP14)
COL_PINS = (board.GP13, board.GP12)

# Bit del reporte para cada (fila, columna): bit 0 = botón 1 ... bit 3 = botón 4.
#            col 1  col 2
BIT_MAP = (
    (0, 1),  # fila 1 -> botones 1 y 2
    (2, 3),  # fila 2 -> botones 3 y 4
)

DEBUG = True

# Filas: en reposo son entradas sin pull (alta impedancia).
# Al escanear, la fila activa pasa a salida en BAJO.
rows = []
for pin in ROW_PINS:
    r = digitalio.DigitalInOut(pin)
    r.direction = digitalio.Direction.INPUT
    rows.append(r)

# Columnas: entradas con pull-up. Leen False si el botón conecta con la fila activa.
cols = []
for pin in COL_PINS:
    c = digitalio.DigitalInOut(pin)
    c.direction = digitalio.Direction.INPUT
    c.pull = digitalio.Pull.UP
    cols.append(c)

report = bytearray(1)


def scan_matrix():
    """Devuelve el byte con un bit a 1 por cada botón pulsado."""
    buttons = 0
    for ri, row in enumerate(rows):
        row.switch_to_output(value=False)
        time.sleep(0.0001)
        for ci, col in enumerate(cols):
            if not col.value:  # False = conectado a la fila activa (en bajo)
                buttons |= 1 << BIT_MAP[ri][ci]
        row.switch_to_input()  # devuelve la fila a reposo (alta impedancia)
    return buttons


def send(buttons):
    report[0] = buttons
    gamepad.send_report(report)


# Reporte inicial (todo suelto). Si el host aún no está listo, reintenta.
try:
    send(0)
except OSError:
    time.sleep(1)
    send(0)

previous = 0

while True:
    current = scan_matrix()
    if current != previous:
        send(current)
        if DEBUG:
            print("botones:", "{:04b}".format(current))
        previous = current
    time.sleep(0.005)