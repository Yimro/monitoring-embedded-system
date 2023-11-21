# monitoring-embedded-system
This project is about a monitoring stack that is running on an embedded system. My stack is running on a RP Zero W V1.1 with an ARMv6 CPU and 512 K RAM. The Zero is used to monitor
- a NAS through Prometheus SNMP Exporter
- itself through Prometheus Node Exporter
- some sensors through my homegrown Custom Exporter
I am not commenting on the SNMP Exporter and Node Exporter as they are pretty much self explaining. Here my code for the sensors and the custom exporter is published.

The custom exporter is written in Python. One sensor is running MicroPython, another sensor is running on C++.


### custom-exporter-sensors
Python exporter for the sensors, using the python prometheus library. This exporter fetches data as a MQTT subscriber and makes them srcapable for Prometheus.

### images
Some photos

### sensor-node-pico-dht20
Temperature and humidity sensor based on a Raspberry Pico W, written in MicroPython.
Publishes data (temperature # humidity, crc) every few seconds to a MQTT Broker.

### sensor-node-esp32-mhz19
CO2-Sensor connected to a ESP32. Written in C++. Publishes values via MQTT Broker
