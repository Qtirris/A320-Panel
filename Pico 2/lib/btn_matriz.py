import digitalio
import board
import time

#Las filas deben ir en OUTPUT LOW
pin_filas=[board.GP10,board.GP11]#,board.GP12,board.GP13,board.GP14
#Las columnas deben ir en INPUT PULLUP
pin_columnas=[board.GP0,board.GP1,board.GP2,board.GP3,board.GP4]#,board.GP5,board.GP6,board.GP7,board.GP8,board.GP9


filas=[] #Objetos DigitalioInOut
columnas=[] #Objetos DigitalioInOut

matriz = [[ 0 for _ in pin_columnas] for _ in pin_filas] #Matriz de estados

cambio=False




def iniciar_matriz():
    '''
    Asigna los objetos DigitalInOut de los pines en INPUT a las listas
    '''
    for pin in pin_filas:
        f=digitalio.DigitalInOut(pin)
        f.direction=digitalio.Direction.INPUT
        filas.append(f)

    for pospin, pin in enumerate(pin_columnas):
        c=digitalio.DigitalInOut(pin)
        c.direction=digitalio.Direction.INPUT
        columnas.append(c)


def escanear_matriz():
    '''
    Recorre la matriz leyendo el estado de la columna en INPUT PULLUP con su respectiva fila en OUTPUT LOW
    '''
    global cambio
    for posf , f in enumerate(filas):
        f.switch_to_output()
        time.sleep(0.0001)   
        f.value=0 #OUTPUT LOW
        for posc, c in enumerate(columnas):
            c.pull=digitalio.Pull.UP #INPUT PULLUP
            if matriz[posf][posc]!=int(c.value):
                matriz[posf][posc]=int(c.value)
                cambio=True
            c.direction=digitalio.Direction.INPUT
        f.direction=digitalio.Direction.INPUT
    imprimir_matriz()
        
def imprimir_matriz():
    '''
    Solo imprime si hubo un cambio en la matriz de estados
    '''
    global cambio
    if cambio:
        cambio=False
        for f in matriz:
            print(f)
        print("-----------")
