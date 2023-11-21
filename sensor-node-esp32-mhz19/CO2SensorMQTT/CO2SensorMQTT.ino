#include <Arduino.h>
#include "MHZ19.h"                                        
#include <SoftwareSerial.h>                                // Remove if using HardwareSerial
#include <WiFi.h>
#include <PubSubClient.h>

#define RX_PIN 17                                          // Rx pin which the MHZ19 Tx pin is attached to
#define TX_PIN 16                                          // Tx pin which the MHZ19 Rx pin is attached to
#define BAUDRATE 9600                                      // Device to MH-Z19 Serial baudrate (should not be changed)

const char* ssid     = "GG2EC"; // Change this to your WiFi SSID
const char* password = "31760502175326880297"; // Change this to your WiFi password
const char* mqtt_server = "10.0.0.114";
const char* out_topic = "node2/values";
const char* in_topic = "node2/commands";

MHZ19 myMHZ19;                                             // Constructor for library
//SoftwareSerial mySerial(RX_PIN, TX_PIN);                   // (Uno example) create device to MH-Z19 serial

unsigned long getDataTimer = 0;

WiFiClient espClient;
PubSubClient client(espClient);

void callback(char* topic, byte* payload, unsigned int length) {
  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.print("] ");
  for (int i=0;i<length;i++) {
    Serial.print((char)payload[i]);
  }
  Serial.println();
}

void connect_wifi()
{
    Serial.println();
    Serial.println("******************************************************");
    Serial.print("Connecting to ");
    Serial.println(ssid);

    WiFi.begin(ssid, password);

    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }

    Serial.println("");
    Serial.println("WiFi connected");
    Serial.print("IP address: ");
    Serial.println(WiFi.localIP());
}



void reconnect(){
    while (!client.connected()){
      Serial.println("Attempting MQTT connection...");
      if (client.connect("ESP32-CO2")){
        Serial.println("connected");
        client.publish(out_topic, "hello i just connected");
        client.subscribe(in_topic);
      } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" Try again in 5 secs");
      delay(5000);
      }
    }

}
void setup()
{
    Serial.begin(9600);                                     // Device to serial monitor feedback
    //while(!Serial){delay(100);}
    
    client.setServer(mqtt_server, 1883);
    client.setCallback(callback);
    connect_wifi();
    delay(300);
    
    Serial2.begin(9600, SERIAL_8N1, RX_PIN, TX_PIN);       // Start Serial2
    myMHZ19.begin(Serial2);                                // *Serial(Stream) refence must be passed to library begin(). 
    myMHZ19.autoCalibration();                              // Turn auto calibration ON (OFF autoCalibration(false))
}

void loop()
{
    if (!client.connected()) {reconnect();}
    client.loop(); // initialize mqtt client
    
    if (millis() - getDataTimer >= 2000)
    {
        int CO2; 

        /* note: getCO2() default is command "CO2 Unlimited". This returns the correct CO2 reading even 
        if below background CO2 levels or above range (useful to validate sensor). You can use the 
        usual documented command with getCO2(false) */

        CO2 = myMHZ19.getCO2();                             // Request CO2 (as ppm)
        
        Serial.print("CO2 (ppm): ");                      
        Serial.println(CO2);                                

        int8_t Temp;
        Temp = myMHZ19.getTemperature();                     // Request Temperature (as Celsius)
        Serial.print("Temperature (C): ");                  
        Serial.println(Temp);       

        char json_str[40]; // Convert to char
        snprintf(json_str, sizeof(json_str), "{\"co2\":%d, \"t\":%d}", CO2, Temp);
        //itoa(CO2, co2str, 10); // convert to char
        
        client.publish("node2/values", json_str); // MQTT Publish CO2 value

        getDataTimer = millis();
    }
}
