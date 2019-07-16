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


LCD_INSTR_WRITE_DATA = 0b00000000
LCD_INSTR_DISPLAY_CLEAR = 0b00000001
LCD_INSTR_RETURN_HOME = 0b00000010
LCD_INSTR_ENTRY_MODE_SET = 0b00000100 
LCD_INSTR_DISPLAY_ON_OFF = 0b00001000
LCD_INSTR_CURSOR_OR_DISPLAY_SHIFT = 0b00010000
LCD_INSTR_FUNCTION_SET = 0b00100000
LCD_INSTR_CGRAM_SET = 0b01000000
LCD_INSTR_DDRAM_SET = 0b10000000

LCD_LONG_WAIT_S = 0.0016 # 160us
LCD_SHORT_WAIT_S = 0.00004 # 40 us

class Instruction:
    """
    Represent a single instruction for the HD44780 controller.

    :param instr: The instruction code to be written on the D7...D0 pins
    :param RS: The value of the register select pin (LCD_RS_CMD or LCD_RS_DATA)
    :param RW: The value of the read-write pin (LCD_RW_READ or LCD_RW_WRITE)
    :param wait: The time it takes this instruction to complete, in seconds.
    """
    def __init__(self, instr, params = 0, RS=LCD_RS_CMD, RW=LCD_RW_WRITE, wait=LCD_SHORT_WAIT_S):
        self.RS = RS
        self.RW = RW
        self.instr = instr
        self.params = params
        self.wait = wait
    
    def high_byte(self):
        """
        Helper function that returns a high order byte corresponding to
        D7...D4, 0, 0, RW, RS
        for writing to the HD44780 controller in 4 bits mode
        """
        return self.RS | self.RW | ((self.instr | self.params) & 0xF0)
    
    def low_byte(self):
        """
        Helper function that returns a low order byte corresponding to
        D3...D0, 0, 0, RW, RS
        for writing to the HD44780 controller in 4 bits mode

        :param enable: Whether the enable bit should be set to LCD_E_ENABLE or LCD_E_DISABLE
        :param backlight: Whether the backlight should be turned on or off
        """
        return self.RS | self.RW | (((self.instr | self.params) & 0x0F) << 4)

    def completion_time_s(self):
        return self.wait

class InstructionFactory:
    """
    See HD44780 datasheet, p24
    """

    @staticmethod
    def clear_display():
        return Instruction(LCD_INSTR_DISPLAY_CLEAR, wait=LCD_LONG_WAIT_S)

    @staticmethod
    def return_home():
        return Instruction(LCD_INSTR_RETURN_HOME, wait=LCD_LONG_WAIT_S)

    @staticmethod
    def entry_mode_set(increment=LCD_INCREMENT, shift=LCD_SHIFT_OFF):
        return Instruction(LCD_INSTR_ENTRY_MODE_SET, increment | shift)

    @staticmethod
    def display_on_off(display=LCD_DISPLAY_ON, cursor=LCD_CURSOR_OFF, blinking=LCD_BLINKING_OFF):
        return Instruction(LCD_INSTR_DISPLAY_ON_OFF, display | cursor | blinking)

    @staticmethod
    def cursor_or_display_shift(display_or_cursor=LCD_CURSOR, left_or_right=LCD_LEFT):
        return Instruction(LCD_INSTR_CURSOR_OR_DISPLAY_SHIFT, display_or_cursor | left_or_right)

    @staticmethod
    def function_set(data_length=LCD_4_BITS, lines=LCD_LINES_2, font=LCD_FONT_8x5):
        if lines == LCD_LINES_2 and font == LCD_FONT_10x5:
            raise ValueError("Invalid parameters: cannot display two lines for 5x10 font")

        return Instruction(LCD_INSTR_FUNCTION_SET, data_length | lines | font)

    @staticmethod
    def set_cgram_address(address):
        if address < 0 or address > 0b111111:
            raise ValueError("Invalid parameter: address must be in the range 0x00 to 0x3f")

        return Instruction(LCD_INSTR_CGRAM_SET, address)

    @staticmethod
    def set_ddram_address(address):
        if address < 0 or address > 0b1111111:
            raise ValueError("Invalid parameter: address must be in the range 0x00 to 0x7f")

        return Instruction(LCD_INSTR_DDRAM_SET, address)

    @staticmethod
    def write_data(data):
        if data < 0 or data > 0xff:
            raise ValueError("Invalid parameter: data must be in the range 0x00 to 0xff")

        return Instruction(LCD_INSTR_WRITE_DATA, data, RS=LCD_RS_DATA)

    #TODO: There are two missing instructions:
    #      - Read busy flag & address instruction
    #      - Read data instruction
    #      For these, we need to make sure there isn't going to be contention on the port.


