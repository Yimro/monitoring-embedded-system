# configuration settings for the sensor node
# all config only here, no hard coding

# network settings:
IP = '10.0.0.122'
SUBMASK = '255.255.254.0'
GATEWAY = '10.0.0.1'
DNS = '10.0.0.1'

# environment / dht20 Pin settings:
SDA = 4 # I2C SDA
SCL = 5 # I2C SCL

# display Pin settings:
MOSI = 19 # SPI MOSI
SCK = 18 # SPI SCK
DC = 17 # Data / Command
CS = 16 # Chip Select
RST = 20 # Reset

# mqtt settings:
MQTT_CLIENT_ID = 'node_1'
# MQTT_BROKER_ADDR = '10.0.0.103' # address of mqtt broker
# MQTT_BROKER_ADDR = 'test.mosquitto.org' # address of mqtt broker
MQTT_BROKER_ADDR = '10.0.0.114'
MQTT_BROKER_PORT = 1883
MQTT_PUBLISH_TOPIC = 'node_1/values'
MQTT_SUBSCRIBE_TOPIC = 'node_1/commands'
