"""
Lectura de la matriz de switches y conversión a botones del gamepad.

Tipos de elemento (se declaran en ELEMENTOS):
  "btn": botón o switch con estado mantenido. 1 contacto -> 1 botón (1 mientras esté accionado).
  "sw2": switch de 2 posiciones. 1 contacto -> 2 botones con pulso:
         botón base   = pulso al pasar a ON
         botón base+1 = pulso al pasar a OFF
  "sw3": switch de 3 posiciones. 2 contactos (c = arriba, c+1 = abajo) -> 2 botones con pulso:
         botón base   = pulso al subir una posición
         botón base+1 = pulso al bajar una posición

Los botones del gamepad se numeran en el orden de ELEMENTOS (el primero es el botón 1).
Ejecuta describir() para ver la tabla de asignación.
"""

import digitalio
import board
import time

# Filas: OUTPUT LOW al escanear. Columnas: INPUT con PULL UP.
pin_filas = [board.GP10, board.GP11]
pin_columnas = [board.GP0, board.GP1, board.GP2, board.GP3, board.GP4, board.GP5, board.GP6, board.GP7, board.GP8, board.GP9]
NUM_FILAS = len(pin_filas)
NUM_COLUMNAS = len(pin_columnas)

PULSO_NS = 80_000_000  # duración del pulso: 50 ms
MAX_BOTONES = 46       # debe coincidir con el descriptor de boot.py

# (tipo, fila, columna)  -> para "sw3", la columna es la de "arriba"
ELEMENTOS = [
    ("sw2", 0, 0),
    ("sw3", 0, 1),
    ("sw2", 0, 3),
    ("sw3", 0, 4),
    ("sw3", 0, 6),
    ("sw3", 0, 8),
    ("sw2", 1, 0),
    ("sw3", 1, 1),
    ("sw2", 1, 3),
    ("sw2", 1, 4),
    ("sw2", 1, 5),
    ("sw2", 1, 6),
    ("sw2", 1, 7),
    ("sw3", 1, 8)
]

_ANCHO = {"btn": 1, "sw2": 2, "sw3": 2}

# Primer botón de cada elemento
_base = []
_n = 0
for _tipo, _f, _c in ELEMENTOS:
    if _tipo not in _ANCHO:
        raise ValueError("Tipo desconocido: %s" % _tipo)
    if _tipo == "sw3" and _c + 1 >= NUM_COLUMNAS:
        raise ValueError("sw3 en columna %d se sale de la matriz" % _c)
    _base.append(_n)
    _n += _ANCHO[_tipo]
NUM_CMD = _n
if NUM_CMD > MAX_BOTONES:
    raise ValueError("Hay %d botones y el descriptor solo tiene %d" % (NUM_CMD, MAX_BOTONES))

filas = []
columnas = []

matriz_sw_anterior = [[0] * NUM_COLUMNAS for _ in range(NUM_FILAS)]
matriz_sw_actual = [[0] * NUM_COLUMNAS for _ in range(NUM_FILAS)]

cmd = [0] * NUM_CMD    # lista plana de botones: es lo que se le pasa a Panel
_fin_pulso = [0] * NUM_CMD


def iniciar_matriz():
    """Configura los pines y hace una lectura inicial sin generar pulsos."""
    for pin in pin_filas:
        f = digitalio.DigitalInOut(pin)
        f.direction = digitalio.Direction.INPUT  # alta impedancia
        filas.append(f)
    for pin in pin_columnas:
        c = digitalio.DigitalInOut(pin)
        c.direction = digitalio.Direction.INPUT
        c.pull = digitalio.Pull.UP
        columnas.append(c)
    escanear_matriz()
    for f in range(NUM_FILAS):
        matriz_sw_anterior[f][:] = matriz_sw_actual[f]


def escanear_matriz():
    """Contacto cerrado = 1 (con pull-up, el contacto cerrado lee 0)."""
    for posf, f in enumerate(filas):
        f.switch_to_output(value=False)
        time.sleep(0.0001)
        for posc, c in enumerate(columnas):
            matriz_sw_actual[posf][posc] = 0 if c.value else 1
        f.switch_to_input()


def _posicion(m, f, c):
    """Posición de un sw3: 0 = arriba, 1 = medio, 2 = abajo."""
    if m[f][c]:
        return 0
    if m[f][c + 1]:
        return 2
    return 1


def _pulso(activar, cancelar, t):
    """Inicia el pulso del botón 'activar' y anula el del opuesto."""
    _fin_pulso[activar] = t + PULSO_NS
    _fin_pulso[cancelar] = 0


def escanear_comandos():
    """Rellena la lista cmd a partir de la matriz anterior y la actual."""
    t = time.monotonic_ns()

    for i, (tipo, f, c) in enumerate(ELEMENTOS):
        b = _base[i]

        if tipo == "btn":
            cmd[b] = matriz_sw_actual[f][c]
            continue

        if tipo == "sw2":
            antes = matriz_sw_anterior[f][c]
            ahora = matriz_sw_actual[f][c]
            if ahora and not antes:
                _pulso(b, b + 1, t)      # pasó a ON
            elif antes and not ahora:
                _pulso(b + 1, b, t)      # pasó a OFF
        else:  # "sw3"
            antes = _posicion(matriz_sw_anterior, f, c)
            ahora = _posicion(matriz_sw_actual, f, c)
            if ahora < antes:
                _pulso(b, b + 1, t)      # subió
            elif ahora > antes:
                _pulso(b + 1, b, t)      # bajó

        cmd[b] = 1 if t < _fin_pulso[b] else 0
        cmd[b + 1] = 1 if t < _fin_pulso[b + 1] else 0

    for f in range(NUM_FILAS):
        matriz_sw_anterior[f][:] = matriz_sw_actual[f]


def describir():
    """Imprime qué botón del gamepad corresponde a cada función."""
    for i, (tipo, f, c) in enumerate(ELEMENTOS):
        b = _base[i] + 1  # los botones se numeran desde 1
        if tipo == "btn":
            print("Botón %d: mantenido (fila %d, col %d)" % (b, f, c))
        elif tipo == "sw2":
            print("Botón %d: ON | Botón %d: OFF (fila %d, col %d)" % (b, b + 1, f, c))
        else:
            print("Botón %d: sube | Botón %d: baja (fila %d, cols %d-%d)" % (b, b + 1, f, c, c + 1))
