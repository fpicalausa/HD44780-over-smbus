import smbus
import time

TRANSPORT_DATA_READY_WAIT_S = 0.000005 # The time it takes for a PCF8574 to have stable data on the output.

class ConsoleTransport:
    """
    A dummy transport that writes every byte it receives to the console.
    """

    def __init__(self):
        self.counter = 1

    def __enter__(self):
        return self

    def write_byte(self, byte):
        data = (byte & 0xF0) >> 4
        b = byte & 0b1000
        e = byte & 0b100
        rw = byte & 0b10
        rs = byte & 0b1
        self.counter = self.counter + 1

        if not e:
            return

        print('{0:08b} -> B:{1:d} E:{2:d} RW:{3:d} RS:{4:d} D:{5:04b}'.format(
          byte,
          1 if b else 0,
          1 if e else 0,
          1 if rw else 0,
          1 if rs else 0,
          data
        ))

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self


class SMBusTransport:
    """
    A layer on top of smbus to transport individual bytes to a given bus at a given address.
    """

    def __init__(self,bus_number, address):
        self.bus_number = bus_number
        self.address = address
        self.bus = None

    def __enter__(self): 
        self.bus = smbus.SMBus(self.bus_number)
        return self

    def write_byte(self, byte):
        """
        Write a single byte to the device.

        :param byte: The byte to write to the device. This is expected to be an 
                     integer with value between 0 and 255 (included)
        """
        self.bus.write_byte(self.address, byte)
        time.sleep(TRANSPORT_DATA_READY_WAIT_S)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.bus:
            self.bus.close()