from smbus2 import SMBus


class Ina226:
    def __init__(self):
        self.ADDR = 0x40
        self.REG_SHUNT_V = 0x01
        self.REG_BUS_V = 0x02

    def read_reg(self, bus, reg):
        raw = bus.read_word_data(self.ADDR, reg)
        return ((raw & 0xFF) << 8) | (raw >> 8)

    def get_voltage(self):
        with SMBus(1) as bus:
            bus_v = self.read_reg(bus, self.REG_BUS_V) * 1.25e-3  # convert raw to volts
            return bus_v