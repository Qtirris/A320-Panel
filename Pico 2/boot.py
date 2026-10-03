# boot.py: gamepad HID de 4 botones, sin ejes.
# Reporte de 1 byte: bits 0-3 = botones 1-4, bits 4-7 = relleno.
# Solo se ejecuta al arrancar la placa (reconecta el USB tras guardarlo).

import usb_hid

GAMEPAD_REPORT_DESCRIPTOR = bytes(
    (
        0x05, 0x01,  # Usage Page (Generic Desktop)
        0x09, 0x05,  # Usage (Game Pad)
        0xA1, 0x01,  # Collection (Application)
        0x85, 0x04,  # Report ID 4
        # 4 botones
        0x05, 0x09,  # Usage Page (Button)
        0x19, 0x01,  # Usage Minimum (Button 1)
        0x29, 0x04,  # Usage Maximum (Button 4)
        0x15, 0x00,  # Logical Minimum (0)
        0x25, 0x01,  # Logical Maximum (1)
        0x75, 0x01,  # Report Size (1 bit)
        0x95, 0x04,  # Report Count (4)
        0x81, 0x02,  # Input (Data, Var, Abs)
        # 4 bits de relleno para completar el byte
        0x75, 0x01,  # Report Size (1 bit)
        0x95, 0x04,  # Report Count (4)
        0x81, 0x03,  # Input (Const, Var, Abs)
        0xC0,        # End Collection
    )
)

gamepad = usb_hid.Device(
    report_descriptor=GAMEPAD_REPORT_DESCRIPTOR,
    usage_page=0x01,
    usage=0x05,
    report_ids=(4,),
    in_report_lengths=(1,),
    out_report_lengths=(0,),
)

usb_hid.enable((gamepad,))