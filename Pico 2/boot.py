import usb_hid

GAMEPAD_REPORT_DESCRIPTOR = bytes(
    (
        0x05, 0x01,  # Usage Page (Generic Desktop)
        0x09, 0x05,  # Usage (Game Pad)
        0xA1, 0x01,  # Open Collection (Application)
        0x85, 0x04,  # Report ID 4
        # 64 botones
        0x05, 0x09,  # Usage Page (Button)
        0x19, 0x01,  # Usage Minimum (Button 1)
        0x29, 0x40,  # Usage Maximum (Button 64)
        0x15, 0x00,  # Logical Minimum (0)
        0x25, 0x01,  # Logical Maximum (1)
        0x75, 0x01,  # Report Size (1 bit)
        0x95, 0x2E,  # Report Count (46)
        0x81, 0x02,  # Input (Data, Var, Abs)
        0xC0,        # End Collection
    )
)

gamepad = usb_hid.Device(
    report_descriptor=GAMEPAD_REPORT_DESCRIPTOR,
    usage_page=0x01,
    usage=0x05,
    report_ids=(4,),
    in_report_lengths=(8,), #Longitud de cuantos bytes estoy usando (Report Count x Report Size)
    out_report_lengths=(0,),
)

usb_hid.enable((gamepad,))