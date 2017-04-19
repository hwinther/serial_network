#include <IRremote.h>

IRsend irsend;
int incomingByte = 0;

void setup() {
  Serial.begin(57600);
  Serial.println("Init");
}

void loop() {
  if (Serial.available() > 0) {
    incomingByte = Serial.read();

    Serial.print("I received: ");
    Serial.println(incomingByte, DEC);

    //(int) strtol(str, 0, 16)
    unsigned long data = 0x20DF10EF;

    if (incomingByte == 10)
    {
      Serial.print("Sending code: ");
      Serial.println(data, HEX);
      //for (int i = 0; i < 3; i++)
      //{
        //irsend.sendRC6(sendCode, 20);
        irsend.sendNEC(data, 32);
        //delay(40);
      //}
    }
  }
}
