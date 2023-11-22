# built-in libraries:
from machine import Pin, I2C, Timer, WDT, Pin
from time import sleep_ms
import network, socket, gc, json

# external libraries:
from umqtt.simple2 import MQTTClient

# home made libraries:
import wifi
import environment
import config

class Node:
    def __init__(self):
        self.ip = self.connect_wlan('10.0.0.122', '255.255.254.0', '10.0.0.1', '10.0.0.1')
        self.env = environment.Env()
        self.display = None
        sleep_ms(100)
        self.mqtt_client = MQTTClient(config.MQTT_CLIENT_ID, config.MQTT_BROKER_ADDR, port=1883)
        self.mqtt_client.connect()

    def connect_wlan(self, ip, mask, gateway, dns):
        print("Connecting to wifi ...")
        self.station = network.WLAN(network.STA_IF)
        self.station.active(True)
        self.station.connect(wifi.ssid, wifi.password)
        print('Wifi connection OK ', end = "")
        self.station.ifconfig((ip, mask, gateway, dns))
        sleep_ms(100)
        print(self.station.ifconfig())
        return self.station.ifconfig()[0]

    def set_display(self, display:display.Display) -> None:
        self.display = display

    def publish_values(self):
        raw_values = self.env.get_values()
        json_values = json.dumps(raw_values).encode('utf-8')
        print('publishing to broker ' + config.MQTT_BROKER_ADDR, end=': ')
        self.mqtt_client.publish(config.MQTT_PUBLISH_TOPIC, json_values)

def loop():
    myNode = Node()
    sleep_ms(1000)
    myWDT = WDT(timeout=7000)
    while True:

        led = Pin("LED", Pin.OUT)
        led.value(1)
        sleep_ms(100)
        led.value(0)

        d = myNode.env.get_values()
        print(d)
        myNode.publish_values()
        myWDT.feed()
        sleep_ms(2900)
