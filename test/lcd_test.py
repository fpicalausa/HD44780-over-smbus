import time
from hd44780 import HD44780, LCD_E_ENABLE, LCD_BACKLIGHT_OFF

class FakeTransport:
    def __init__(self):
        self.bytes = []

    def write_byte(self, byte):
        self.bytes.append(byte)

def toggle_enable(byte):
    return [
        byte,
        byte | LCD_E_ENABLE,
        byte
    ]

def test_lcd_initialization():
    t = FakeTransport()
    lcd = HD44780(t, backlight=LCD_BACKLIGHT_OFF)
    lcd.init_lcd()

    expected = (
        toggle_enable(0b0011_0000) * 3 +
        # 4bits mode set
        toggle_enable(0b0010_0000) + 
        # 4bits mode set, 2 lines, 8x5 font
        toggle_enable(0b0010_0000) + 
        toggle_enable(0b1000_0000) + 
        # display off
        toggle_enable(0b0000_0000) + 
        toggle_enable(0b1000_0000) + 
        # clear screen
        toggle_enable(0b0000_0000) + 
        toggle_enable(0b0001_0000) + 
        # entry mode set
        toggle_enable(0b0000_0000) + 
        toggle_enable(0b0110_0000) 
    )

    assert t.bytes == expected