﻿# monitoring-embedded-system
This project is about a monitoring stack that is running on an embedded system. My stack is running on a RP Zero W V1.1 with an ARMv6 CPU and 512 K RAM. The Zero is used to monitor
- a NAS through Prometheus SNMP Exporter
- itself through Prometheus Node Exporter
- some sensors through my homegrown Custom Exporter

I am not commenting on the SNMP Exporter and Node Exporter as they are pretty much self explaining. Here my code for the sensors and the custom exporter is published.

The custom exporter is written in Python. It imports data from sensors, _sensor-node-pico-dht20_ and _sensor-node-esp32-mhz20_.


### custom-exporter-sensors
Python exporter for the sensor nodes, uses the python prometheus exporter library. This exporter receives data as a MQTT subscriber and exports them.

### custom-exporter-loadtest
Python script that generates many exporters and a http service discovery server

### setup 1 - overview
![Schematic overview of project setup 1](https://github.com/Yimro/monitoring-embedded-system/blob/main/images/overview-setup-1.png)


### setup 2 - overview
![Schematic overview of project setup 2](https://github.com/Yimro/monitoring-embedded-system/blob/main/images/overview-setup-2.png)

### sensor-node-pico-dht20
Temperature and humidity sensor based on a Raspberry Pico W, written in MicroPython.
Publishes data (temperature # humidity, crc) every few seconds to a MQTT Broker.

### sensor-node-esp32-mhz19
CO2-Sensor connected to a ESP32. Written in C++. Publishes values via MQTT Broker
