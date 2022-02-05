#include <LoRa.h>
#include <stdint.h>

#define CS_PIN 18
#define RST_PIN 23
#define IRQ_PIN 26
#define expected_packet_size 255

void setup() {
  // put your setup code here, to run once:
  Serial.begin(1152000);
  while(!Serial);

  LoRa.setPins(CS_PIN, RST_PIN, IRQ_PIN);
  if(!LoRa.begin(915E6))
  {
    Serial.println("LoRa init failed. Check your connections");
    while(true);
  }

  LoRa.disableCrc();
  LoRa.setOCP(240);
  //LoRa.setGain(4);
  LoRa.setSignalBandwidth(500E3);
}

void loop() {
  while(Serial.available() == 0);
    char input = (char) Serial.read(); // Clear
    if(input == 'r')
    {
      clear_buffer();
      configure_radio();
    }
}

void onReceive(int packetSize)
{
  int read_len = LoRa.available();
  
  if(read_len == 0)
    return;
  
  Serial.print(LoRa.packetRssi());
  Serial.print(" ");
  Serial.print(LoRa.packetSnr());
  Serial.print(" ");
  Serial.print(read_len);
  Serial.print(" ");

  for(int i = 0; i < read_len; i++)
  {
    Serial.print(LoRa.read(), HEX);
  }

  Serial.println("");
}

void configure_radio()
{
    // Put the radio into standby to update
    LoRa.idle();

    // Set the Coding Rate
    Serial.println("Enter number of redundancy bits: 1, 2, 3, 4");
    clear_buffer();
    while(Serial.available() == 0);
    int coding_rate = Serial.parseInt();
    Serial.print("Setting coding rate to ");
    Serial.println(coding_rate);
    LoRa.setCodingRate4(coding_rate);
    
    Serial.println("Enter spreading factor: 6, 7, 8, 9, 10, 11, 12");
    clear_buffer();
    while(Serial.available() == 0);
    int spreading_factor = Serial.parseInt();
    LoRa.setSpreadingFactor(spreading_factor);
    Serial.print("Set spreading factor to ");
    Serial.println(LoRa.getSpreadingFactor(), HEX);
    Serial.print("Current bandwidth: ");
    Serial.print(LoRa.getSignalBandwidth(), HEX);

    LoRa.onReceive(onReceive);
    LoRa.receive();
}

void clear_buffer()
{
    while(Serial.available() > 0)
        Serial.read();
}
