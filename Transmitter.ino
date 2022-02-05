
#include <LoRa.h>
#include <stdint.h>

#define CS_PIN 18
#define RST_PIN 23
#define IRQ_PIN 26
#define expected_packet_size 255

uint8_t data_packet[255];
uint8_t sent_flag;

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
  LoRa.setTxPower(20);
  LoRa.setOCP(240);
  LoRa.setSignalBandwidth(500E3);
}

void loop() {
  // put your main code here, to run repeatedly:
    //Serial.println("Press enter to send a message");
    clear_buffer();
    while(Serial.available() == 0);
    char input = (char) Serial.read(); // Clear
    if(input == 'e')
      while(true);
    else if(input == 'r')
    {
      configure_radio();
    }
    else
    {
      generate_random_packet();
      LoRa.beginPacket(false); // By adding true we are implying that we want the implicit header style
      LoRa.write(data_packet, 255);
      LoRa.endPacket(false);
    }
}

void generate_random_packet()
{
  for(int i = 0; i < 255; i++)
  {
    data_packet[i] = (uint8_t) random(0, 15);
    Serial.print(data_packet[i], HEX);
  }

  Serial.println(" 255");
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
}

void clear_buffer()
{
    while(Serial.available() > 0)
        Serial.read();
}
  