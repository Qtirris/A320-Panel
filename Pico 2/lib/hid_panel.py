import struct
import time

from adafruit_hid import find_device

NUM_BOTONES = 46  # debe coincidir con Usage Maximum / Report Count de boot.py


class Panel:
    """Panel de botones que se presenta al PC como un gamepad HID.

    El estado se envía en un reporte de 8 bytes (64 bits):

    - Bits 0 a NUM_BOTONES-1: un bit por botón (1 = pulsado). El bit 0 es el botón 1.
    - Bits restantes: relleno, siempre 0.

    Debe coincidir con el descriptor de ``boot.py`` (``in_report_lengths=(8,)``).
    Solo se envía un reporte cuando el estado cambia respecto al último.
    """

    def __init__(self, devices):
        """Busca el dispositivo HID y envía un reporte inicial con todo suelto.

        :raises ValueError: si ningún dispositivo tiene usage_page 0x01 y usage 0x05.
        Si el HID aún no está listo (OSError), espera 1 s y reintenta una vez.
        """
        self._gamepad_device = find_device(devices, usage_page=0x01, usage=0x05)
        self._report = bytearray(8)
        self._last_report = bytearray(8)
        self._state = 0

        try:
            self.reset_all()
        except OSError:
            time.sleep(1)
            self.reset_all()

    def switch_update(self, botones):
        """Actualiza el estado de todos los botones.

        :param botones: lista plana de 0/1 (o bool). El elemento i es el botón i+1.
            Puede ser más corta que NUM_BOTONES; los restantes quedan en 0.
        :raises ValueError: si tiene más de NUM_BOTONES elementos.

        Ejemplo::

            panel.switch_update([0, 1, 1, 0])
            # botones 2 y 3 pulsados
        """
        if len(botones) > NUM_BOTONES:
            raise ValueError("Máximo %d botones" % NUM_BOTONES)

        estado = 0
        for i, valor in enumerate(botones):
            if valor:
                estado |= 1 << i

        self._state = estado
        self._send()

    def reset_all(self):
        """Suelta todos los botones y envía el reporte siempre."""
        self._state = 0
        self._send(always=True)

    def _send(self, always=False):
        """Empaqueta el estado y lo envía si hubo cambios (o si always es True)."""
        struct.pack_into("<Q", self._report, 0, self._state)
        if always or self._report != self._last_report:
            self._gamepad_device.send_report(self._report)
            self._last_report[:] = self._report