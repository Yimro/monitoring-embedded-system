#!/usr/bin/env python3

from prometheus_client import start_http_server, Gauge
import json
import paho.mqtt.client as client
import config
import threading

class MQTT_subscriber:
    def __init__(self, hostname, port, timeout, topic):
        self.client = client.Client()
        self.topic = topic
        self.client.connect(hostname, port, timeout)
        self.client.on_connect = self.on_connect

        '''
        below: discerning between the 2 sensor nodes here, generating different
        timeseries for each sensor and setting different callbacks for
        updating the Gauge objects:
        '''

        if self.topic == 'node1/values':
            self.rh_dht20 = Gauge('sensor_rel_humidity_dht20', 'relative humidity in percent by DHT20')
            self.temp_dht20 = Gauge('sensor_temperature_celcius_dht20', 'temperature in degrees Celsius by DHT20')
            self.client.on_message = self.on_message_dht20
        if self.topic == 'node2/values':
            self.temp_mhz19 = Gauge('sensor_temperature_celcius_mhz19', 'temperature in degrees Celsius by MHZ19')
            self.co2_mhz19 = Gauge('sensor_co2_ppm_mhz19', 'CO2 concentration in ppm by MHT19')
            self.client.on_message = self.on_message_mhz19

        self.client.loop_forever()

    def on_connect(self, cl, userdata, flags, rc):
        print("connected with result code" + str(rc) +"\n")
        self.client.subscribe(self.topic)
        print("subscribed to ... "+self.topic+"\n")

    def on_message_dht20(self, cl, userdata, msg):
        try:
            msg_dict = json.loads(msg.payload)
            rh = msg_dict['rh']
            t = msg_dict['t']
            self.rh_dht20.set(rh)
            self.temp_dht20.set(t)
            print(f'temp_dht20={t}, rh={rh}')
        except json.decoder.JSONDecodeError:
            print("ERROR! could not decode json message. ", end='')
            print(f'payload: {msg.payload}')
        except KeyError:
            print("Key error: key does not exist in dictionary")

    def on_message_mhz19(self, cl, userdate, msg):
        try:
            msg_dict = json.loads(msg.payload)
            t = msg_dict['t']
            co2= msg_dict['co2']
            self.temp_mhz19.set(t)
            self.co2_mhz19.set(co2)
            print(f'temp_mhz19={t}, co2={co2}')
        except json.decoder.JSONDecodeError:
            print("ERROR! could not decode json message. ", end='')
            print(f'payload: {msg.payload}')
        except KeyError:
            print("Key error: key does not exist in dictionary")

if __name__ == '__main__':
    # Start up the server to expose the metrics:
    start_http_server(8000)

    # create mqtt subscriber, that receives the node data:

    # 2 subscriber clients running in seperate threads for 2 topics:
    def subscriber1():
        mqs1 = MQTT_subscriber('10.0.0.114', 1883, 60, 'node1/values')

    def subscriber2():
        mqs2 = MQTT_subscriber('10.0.0.114', 1883, 60, 'node2/values')

    thread1 = threading.Thread(target=subscriber1)
    thread2 = threading.Thread(target=subscriber2)

    thread1.start()
    thread2.start()

    thread1.join()
    thread2.join()
