# Diagnóstico de la matriz 2x2 (versión PULL-UP): muestra qué pares de pines están conectados.
# Ejecútalo desde Thonny con Run (no hace falta guardarlo como code.py).
#
# Esperado en reposo:  "Sin conexiones"
# Al pulsar botón 1:   GP15 - GP13
# Al pulsar botón 2:   GP15 - GP12
# Al pulsar botón 3:   GP14 - GP13
# Al pulsar botón 4:   GP14 - GP12

import time

import board
import digitalio

NAMES = ("GP15 (fila 1)", "GP14 (fila 2)", "GP13 (col 1)", "GP12 (col 2)")
PINS = (board.GP15, board.GP14, board.GP13, board.GP12)

pins = [digitalio.DigitalInOut(p) for p in PINS]


def read_connections():
    found = []
    for i, driver in enumerate(pins):
        # Todos los demás como entrada con pull-up
        for j, p in enumerate(pins):
            if j != i:
                p.switch_to_input(pull=digitalio.Pull.UP)
        driver.switch_to_output(value=False)
        time.sleep(0.001)
        for j, p in enumerate(pins):
            if j > i and not p.value:  # False = unido al pin que está en bajo
                found.append(NAMES[i] + "  <->  " + NAMES[j])
        driver.switch_to_input(pull=digitalio.Pull.UP)
    return found


last = None
print("Diagnóstico iniciado. Pulsa botones uno por uno.")
while True:
    current = read_connections()
    if current != last:
        print("-----")
        if current:
            for line in current:
                print("Conectados:", line)
        else:
            print("Sin conexiones")
        last = current
    time.sleep(0.05)
    