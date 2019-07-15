from hd44780 import HD44780, SMBusTransport, ConsoleTransport, InstructionFactory, LCD_DISPLAY_ON

BUS = 1 # Depends on the raspberry pi configuration
DEVICE_ADDRESS = 0x27 # When in doubt, use i2c_detect to figure out where the device is.

def main():
    with SMBusTransport(BUS, DEVICE_ADDRESS) as t:
        lcd = HD44780(t)

        lcd.init_lcd()

        lcd.execute(InstructionFactory.display_on_off(LCD_DISPLAY_ON))
        lcd.execute(InstructionFactory.set_ddram_address(0))
        lcd.execute(InstructionFactory.write_data(0b01001000))
        lcd.execute(InstructionFactory.write_data(0b01100101))
        lcd.execute(InstructionFactory.write_data(0b01101100))
        lcd.execute(InstructionFactory.write_data(0b01101100))
        lcd.execute(InstructionFactory.write_data(0b01101111))

        # From table 5: the first cgram starts at address 0
        lcd.execute(InstructionFactory.set_cgram_address(0b000000))
        lcd.execute(InstructionFactory.write_data(0b00000000))
        lcd.execute(InstructionFactory.write_data(0b00000010))
        lcd.execute(InstructionFactory.write_data(0b00011111))
        lcd.execute(InstructionFactory.write_data(0b00011110))
        lcd.execute(InstructionFactory.write_data(0b00011100))
        lcd.execute(InstructionFactory.write_data(0b00011000))
        lcd.execute(InstructionFactory.write_data(0b00010000))
        lcd.execute(InstructionFactory.write_data(0b00000000))

        lcd.execute(InstructionFactory.set_ddram_address(0x40))
        lcd.execute(InstructionFactory.write_data(0b00100000))
        lcd.execute(InstructionFactory.write_data(0b00100000))
        lcd.execute(InstructionFactory.write_data(0b00000000))
        lcd.execute(InstructionFactory.write_data(0b00000000))
        lcd.execute(InstructionFactory.write_data(0b00000000))
        lcd.execute(InstructionFactory.write_data(0b00000000))
        lcd.execute(InstructionFactory.write_data(0b00000000))
        lcd.execute(InstructionFactory.write_data(0b00000000))
        lcd.execute(InstructionFactory.write_data(0b00000000))
        lcd.execute(InstructionFactory.write_data(0b00000000))

if __name__ == "__main__":
    main()

    1 + 1