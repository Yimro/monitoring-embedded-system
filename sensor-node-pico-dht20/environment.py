'''Simple class for accessing the dht20 sensor via i2c'''

from dht20 import DHT20
from machine import Pin, I2C
import config
import time
class Env:
    def __init__(self):
        self.i2c0_sda = Pin(config.SDA)
        self.i2c0_scl = Pin(config.SCL)
        self.i2c0 = I2C(0, sda=self.i2c0_sda, scl=self.i2c0_scl)
        time.sleep_ms(100) # dht20 object would return OSError EIO without sleep time
        self.dht20 = DHT20(0x38, self.i2c0) # environment sensor on i2c interface
        print("Environment node OK")
        
        
    def get_values(self) -> dict:
        return self.dht20.measurements