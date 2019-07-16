from hd44780 import Instruction, LCD_INSTR_FUNCTION_SET, LCD_4_BITS, LCD_LINES_2, LCD_FONT_8x5

def test_instruction_high_byte():
    # INSTR = 0b00101000 RW = 0 RS = 0
    fs = Instruction(LCD_INSTR_FUNCTION_SET, LCD_4_BITS | LCD_FONT_8x5 | LCD_LINES_2)
    hi = fs.high_byte()
    assert hi == 0b00100000 


def test_instruction_low_byte():
    # INSTR = 0b00101000 RW = 0 RS = 0
    fs = Instruction(LCD_INSTR_FUNCTION_SET, LCD_4_BITS | LCD_FONT_8x5 | LCD_LINES_2)
    lo = fs.low_byte()
    assert lo == 0b10000000  