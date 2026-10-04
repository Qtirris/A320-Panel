import struct
import time

from adafruit_hid import find_device

import btn_matriz as mat

NUM_FILAS = len(mat.pin_filas)
NUM_COLUMNAS = len(mat.pin_columnas)
NUM_SWITCHES = NUM_FILAS * NUM_COLUMNAS


class Panel:
    """Panel de switches y botones que se presenta al PC como un gamepad HID.

    Cada switch de la matriz es un botón del gamepad. El estado completo se
    envía en un reporte de 8 bytes (64 bits) con este formato:

    - Bits 0 a NUM_SWITCHES-1: un bit por switch (1 = ON, 0 = OFF). El bit 0
      es el switch 1.
    - Bits restantes: relleno, siempre 0 (el host los ignora).

    Debe coincidir con el descriptor de ``boot.py``: Usage Maximum y Report
    Count igual a NUM_SWITCHES, relleno hasta 64 bits e
    ``in_report_lengths=(8,)``.

    Solo se envía un reporte cuando el estado cambia respecto al último.
    """

    def __init__(self, devices):
        """Busca el dispositivo HID y envía un reporte inicial con todo en OFF.

        :param devices: lista de dispositivos (normalmente ``usb_hid.devices``)
            o un único dispositivo HID.
        :raises ValueError: si ninguno tiene usage_page 0x01 y usage 0x05
            (Game Pad). Debe coincidir con ``boot.py``.

        Si el HID aún no está listo (OSError), espera 1 segundo y reintenta
        una vez.
        """
        self._gamepad_device = find_device(devices, usage_page=0x01, usage=0x05)
        self._report = bytearray(8)
        self._last_report = bytearray(8)
        self._matrix_state = 0

        try:
            self.reset_all()
        except OSError:
            time.sleep(1)
            self.reset_all()

    def switch_update(self, matrix):
        """Actualiza el estado de todos los switches a partir de la matriz leída.

        Recibe la lectura completa y reconstruye elestado desde cero. 
        Los switches se numeran por filas, empezando en 1: ``sw = fila * NUM_COLUMNAS + columna + 1``.

        :param matrix: lista de filas, cada una con valores 0/1 (o bool),
            de dimensiones NUM_FILAS x NUM_COLUMNAS.
        :raises ValueError: si la matriz no tiene las dimensiones esperadas.

        Ejemplo con una matriz de 2x2::

            panel.switch_update([[0, 1],
                                 [1, 0]])
            # sw1=0, sw2=1, sw3=1, sw4=0
            # estado = 0b0110 -> switches 2 y 3 en ON, 1 y 4 en OFF
        """
        if len(matrix) != NUM_FILAS:
            raise ValueError("La matriz debe tener %d filas" % NUM_FILAS)

        estado = 0
        for posf, valores in enumerate(matrix):
            if len(valores) != NUM_COLUMNAS:
                raise ValueError("Cada fila debe tener %d columnas" % NUM_COLUMNAS)
            for col, valor in enumerate(valores):
                if valor:
                    sw = posf * NUM_COLUMNAS + col + 1
                    estado |= 1 << (self._validate_switch_number(sw) - 1)

        self._matrix_state = estado
        self._send()

    def reset_all(self):
        """Pone todos los switches en OFF y envía el reporte siempre.

        Se envía aunque no haya cambios, para comprobar que el HID responde.
        """
        self._matrix_state = 0
        self._send(always=True)

    def _send(self, always=False):
        """Empaqueta el estado en el reporte y lo envía si hubo cambios.

        :param always: si es True, envía aunque el reporte sea igual al último.
        """
        struct.pack_into("<Q", self._report, 0, self._matrix_state)
        if always or self._report != self._last_report:
            self._gamepad_device.send_report(self._report)
            self._last_report[:] = self._report

    @staticmethod
    def _validate_switch_number(sw):
        """Devuelve ``sw`` si está entre 1 y NUM_SWITCHES; si no, lanza ValueError."""
        if not 1 <= sw <= NUM_SWITCHES:
            raise ValueError("Switch fuera de rango (1 a %d)" % NUM_SWITCHES)
        return sw