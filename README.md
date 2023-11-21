# iot-sensor-monitoring-prometheus
I am working on different setups with prometheus monitoring. Ultimate goal is to let prometheus and grafana run on an embedded system, to start with a RP Zero W

## S0 - setup 0
This is a first setup, containing 4 folders:

### custom-exporter
Python exporter using the prometheus library. This exporter fetches data as a MQTT subscriber.

### images
Todo: Schematics, Photos

### monitoring
The prometheus configuration file, used by Prometheus installation.

### sensor-node
Temperature and humidity sensor based on a Raspberry Pico W, written in MicroPython.
Publishes data (temperature # humidity, crc) every few seconds to a MQTT Broker.chee
