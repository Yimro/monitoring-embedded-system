'''Class for controlling the ss1306 OLED Display'''

from machine import Pin, SPI
from ssd1306 import SSD1306_SPI

class Display:
    def __init__(self):
        self.spi = SPI(0, 100000, mosi=Pin(19), sck=Pin(18)) # spi object for communicating w display
        self.dc = Pin(17) # data / commands
        self.rst = Pin(20) # reset
        self.cs = Pin(16) # chip select
        self.oled = SSD1306_SPI(128, 64, self.spi, self.dc, self.rst, self.cs)
        self.oled.fill(0)
        self.oled.text("initialize OK", 0, 0, 1)
        self.oled.show()
        print("OLED Display OK")

    def update(self, lines:list) -> None:
        self.clear()
        i = 0
        for line in lines:
            self.oled.text(line, 0, i, 1)
            i += 17
        self.oled.show()
    
    def clear(self) -> None:
        self.oled.fill(0)
        self.oled.show()