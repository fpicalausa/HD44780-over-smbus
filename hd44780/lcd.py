import time
from .instructions import *

LCD_ENABLE_CYC_S = 0.000005 # 500ns
LCD_ENABLE_PWEH_S = 0.0000023 # 230ns
LCD_ENABLE_WAIT_S = LCD_ENABLE_PWEH_S
LCD_DISABLE_WAIT_S = LCD_ENABLE_CYC_S - LCD_ENABLE_PWEH_S

LCD_E_ENABLE = 0x4
LCD_E_DISABLE = 0

LCD_BACKLIGHT_ON = 0x8
LCD_BACKLIGHT_OFF = 0

class HD44780:
    def __init__(self, transport, bits=LCD_4_BITS, lines=LCD_LINES_2, font=LCD_FONT_8x5, backlight = LCD_BACKLIGHT_ON):
        if bits == LCD_8_BITS:
            raise NotImplementedError("Not implemented: 8 bits mode")

        self.transport = transport
        self.bits = bits
        self.lines = lines
        self.font = font
        self.backlight = backlight

        # We always start in 8 bits mode
        self.state = LCD_8_BITS

    def init_lcd(self):
        inst_init_mode = InstructionFactory.function_set(LCD_8_BITS, LCD_LINES_1, LCD_FONT_8x5)
        inst_init_mode2 = InstructionFactory.function_set(LCD_4_BITS, LCD_LINES_1, LCD_FONT_8x5)
        inst_user_mode = InstructionFactory.function_set(self.bits, self.lines, self.font)
        inst_display_off = InstructionFactory.display_on_off(LCD_DISPLAY_OFF)
        inst_display_clear = InstructionFactory.clear_display()
        inst_entry_mode = InstructionFactory.entry_mode_set()
       
        time.sleep(0.015) # Wait for more than 15ms after power on -- 
                          # this is not really needed, but doesn't hurt
        self.execute(inst_init_mode) 
        time.sleep(0.0041) # Wait for more than 4.1ms
        self.execute(inst_init_mode) 
        time.sleep(0.0001) # Wait for more than 1 us
        self.execute(inst_init_mode) 
        self.execute(inst_init_mode2) 
        self.state = LCD_4_BITS

        self.execute(inst_user_mode) 
        self.execute(inst_display_off) 
        self.execute(inst_display_clear) 
        self.execute(inst_entry_mode) 
 
    def execute(self, instruction):
        if self.state == LCD_8_BITS:
            self._execute_8bit(instruction)
        else:
            self._execute_4bit(instruction)

    def _execute_8bit(self, instruction):
        hi = instruction.high_byte()
        # Note: we purposely ignore the low byte, since we have no way to write 
        # to our 4 bits interface
        self._send_instruction_part(hi)
        time.sleep(instruction.wait)

    def _execute_4bit(self, instruction):
        hi = instruction.high_byte()
        lo = instruction.low_byte()
        self._send_instruction_part(hi)
        self._send_instruction_part(lo)
        time.sleep(instruction.wait)

    def _send_instruction_part(self, byte):
        t = self.transport
        t.write_byte(byte | self.backlight)
        t.write_byte(byte | self.backlight | LCD_E_ENABLE)
        time.sleep(LCD_ENABLE_WAIT_S)
        t.write_byte(byte | self.backlight)
        time.sleep(LCD_DISABLE_WAIT_S)
