import digitalio
import board
import time

pin_filas = [board.GP10, board.GP11]
pin_columnas = [board.GP0, board.GP1, board.GP2, board.GP3, board.GP4]
NUM_FILAS = len(pin_filas)
NUM_COLUMNAS = len(pin_columnas)

debug=False
cambio=False

filas_3_pos = [0, 1]
columnas_3_pos = [1, 3]      # columna "arriba" ya que "abajo" es la siguiente

PULSO_NS = 35_000_000        # 35 ms

filas = []
columnas = []
matriz_sw_anterior = [[0] * NUM_COLUMNAS for _ in range(NUM_FILAS)]
matriz_sw_actual = [[0] * NUM_COLUMNAS for _ in range(NUM_FILAS)]
matriz_cmd = [[0] * NUM_COLUMNAS for _ in range(NUM_FILAS)]
_fin_pulso = [[0] * NUM_COLUMNAS for _ in range(NUM_FILAS)]


def iniciar_matriz():
    for pin in pin_filas:
        f = digitalio.DigitalInOut(pin)
        f.direction = digitalio.Direction.INPUT      # alta impedancia
        filas.append(f)
    for pin in pin_columnas:
        c = digitalio.DigitalInOut(pin)
        c.direction = digitalio.Direction.INPUT
        c.pull = digitalio.Pull.UP                   # una sola vez
        columnas.append(c)
    # Lectura inicial: evita comandos falsos al arrancar
    escanear_matriz()
    for f in range(NUM_FILAS):
        matriz_sw_anterior[f][:] = matriz_sw_actual[f]


def escanear_matriz():
    """Pulsado/ON = 1 (el contacto cerrado lee 0 por el pull-up)."""
    for posf, f in enumerate(filas):
        f.switch_to_output(value=False)
        time.sleep(0.0001)
        for posc, c in enumerate(columnas):
            matriz_sw_actual[posf][posc] = 0 if c.value else 1
        f.switch_to_input()


def _posicion(m, f, c):
    '''
    Los switches estan conectados de tal manera que se respete la siguiente convención:
    ------------------------------
    Pos    |  Lectura  |  Return
    ------------------------------
    Arriba |  [f][c]   |  -> 2   
    Medio  |  ninguna  |  -> 1   
    Abajo  |  [f][c+1] |  -> 0   
    '''
    if m[f][c]:         # arriba
        return 2        
    if m[f][c + 1]:     # abajo
        return 0        
    return 1            # medio


def escanear_comandos():
    t = time.monotonic_ns() 

    #Reemplazamos toda la matriz por sus comandos
    for f in range(NUM_FILAS):
        matriz_cmd[f][:] = matriz_sw_actual[f]
        

    # Ahora solo los switches de 3 posiciones
    for f in filas_3_pos:
        for c in columnas_3_pos:
            antes = _posicion(matriz_sw_anterior, f, c)
            ahora = _posicion(matriz_sw_actual, f, c)
            if ahora < antes: #bajo
                _fin_pulso[f][c + 1] = t + PULSO_NS
            elif ahora > antes: #subio
                _fin_pulso[f][c] = t + PULSO_NS
            #Si son iguales caen en los casos de abajo
            #_fin_pulso=0 por ende matriz_cmd en esas posiciones será 0
            matriz_cmd[f][c] = 1 if t < _fin_pulso[f][c] else 0
            matriz_cmd[f][c + 1] = 1 if t < _fin_pulso[f][c + 1] else 0

    #Actualizar
    for f in range(NUM_FILAS):
        matriz_sw_anterior[f][:] = matriz_sw_actual[f]
        
def imprimir_comandos():
    '''
    Falta por implementar para el modo debug
    '''
    global cambio
    if cambio:
        for f in matriz_cmd:
            print(f)
    cambio=False