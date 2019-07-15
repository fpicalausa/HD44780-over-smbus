import time

LCD_4_BITS = 0
LCD_8_BITS = 0b10000

LCD_LINES_1 = 0
LCD_LINES_2 = 0b1000

LCD_FONT_8x5 = 0
LCD_FONT_10x5 = 0b100

LCD_DISPLAY_OFF = 0
LCD_DISPLAY_ON = 0b100

LCD_CURSOR_OFF = 0
LCD_CURSOR_ON = 0b10

LCD_CURSOR = 0
LCD_DISPLAY = 0b1000

LCD_LEFT = 0
LCD_RIGHT = 0b100

LCD_BLINKING_OFF = 0
LCD_BLINKING_ON = 0b1

LCD_DECREMENT = 0
LCD_INCREMENT = 0b10

LCD_SHIFT_OFF = 0
LCD_SHIFT_ON = 0b1

LCD_RS_CMD = 0
LCD_RS_DATA = 1

LCD_RW_WRITE = 0
LCD_RW_READ = 0x2

LCD_E_ENABLE = 0x4
LCD_E_DISABLE = 0

LCD_BACKLIGHT_ON = 0x8

LCD_LONG_WAIT_S = 0.0016 # 160us
LCD_SHORT_WAIT_S = 0.00004 # 40 us
LCD_ENABLE_CYC_S = 0.000005 # 500ns
LCD_ENABLE_PWEH_S = 0.0000023 # 230ns
LCD_ENABLE_WAIT_S = LCD_ENABLE_PWEH_S
LCD_DISABLE_WAIT_S = LCD_ENABLE_CYC_S - LCD_ENABLE_PWEH_S

class Instruction:
    """
    Represent a single instruction for the HD44780 controller.

    :param instr: The instruction code to be written on the D7...D0 pins
    :param RS: The value of the register select pin (LCD_RS_CMD or LCD_RS_DATA)
    :param RW: The value of the read-write pin (LCD_RW_READ or LCD_RW_WRITE)
    :param wait: The time it takes this instruction to complete, in seconds.
    """
    def __init__(self, instr, RS=LCD_RS_CMD, RW=LCD_RW_WRITE, wait=LCD_SHORT_WAIT_S):
        self.RS = RS
        self.RW = RW
        self.instr = instr
        self.wait = wait
    
    def high_byte(self):
        """
        Helper function that returns a high order byte corresponding to
        D7...D4, 0, 0, RW, RS
        for writing to the HD44780 controller in 4 bits mode
        """
        return self.RS | self.RW | (self.instr & 0xF0)
    
    def low_byte(self):
        """
        Helper function that returns a low order byte corresponding to
        D3...D0, 0, 0, RW, RS
        for writing to the HD44780 controller in 4 bits mode

        :param enable: Whether the enable bit should be set to LCD_E_ENABLE or LCD_E_DISABLE
        :param backlight: Whether the backlight should be turned on or off
        """
        return self.RS | self.RW | ((self.instr & 0x0F) << 4)

    def completion_time_s(self):
        return self.wait

class InstructionFactory:
    """
    See HD44780 datasheet, p24
    """

    @staticmethod
    def clear_display():
        return Instruction(0b00000001, wait=LCD_LONG_WAIT_S)

    @staticmethod
    def return_home():
        return Instruction(0b00000010, wait=LCD_LONG_WAIT_S)

    @staticmethod
    def entry_mode_set(increment=LCD_INCREMENT, shift=LCD_SHIFT_OFF):
        return Instruction(0b00000100 | increment | shift)

    @staticmethod
    def display_on_off(display=LCD_DISPLAY_ON, cursor=LCD_CURSOR_OFF, blinking=LCD_BLINKING_OFF):
        return Instruction(0b00001000 | display | cursor | blinking)

    @staticmethod
    def cursor_or_display_shift(display_or_cursor=LCD_CURSOR, left_or_right=LCD_LEFT):
        return Instruction(0b00010000 | display_or_cursor | left_or_right)

    @staticmethod
    def function_set(data_length=LCD_4_BITS, lines=LCD_LINES_2, font=LCD_FONT_8x5):
        if lines == LCD_LINES_2 and font == LCD_FONT_10x5:
            raise ValueError("Invalid parameters: cannot display two lines for 5x10 font")

        return Instruction(0b00100000 | data_length | lines | font)

    @staticmethod
    def set_cgram_address(address):
        if address < 0 or address > 0b111111:
            raise ValueError("Invalid parameter: address must be in the range 0x00 to 0x3f")

        return Instruction(0b01000000 | address)

    @staticmethod
    def set_ddram_address(address):
        if address < 0 or address > 0b1111111:
            raise ValueError("Invalid parameter: address must be in the range 0x00 to 0x7f")

        return Instruction(0b10000000 | address)

    @staticmethod
    def write_data(data):
        if data < 0 or data > 0xff:
            raise ValueError("Invalid parameter: data must be in the range 0x00 to 0xff")

        return Instruction(data, RS=LCD_RS_DATA)

    #TODO: There are two missing instructions:
    #      - Read busy flag & address instruction
    #      - Read data instruction
    #      For these, we need to make sure there isn't going to be contention on the port.


class HD44780:
    def __init__(self, transport, bits=LCD_4_BITS, lines=LCD_LINES_2, font=LCD_FONT_8x5):
        if bits == LCD_8_BITS:
            raise NotImplementedError("Not implemented: 8 bits mode")

        self.transport = transport
        self.bits = bits
        self.lines = lines
        self.font = font
        self.backlight = LCD_BACKLIGHT_ON

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
