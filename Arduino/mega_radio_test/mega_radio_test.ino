#include "Packet.h"
#include "Protocol.h"

/**
 * \brief test
 */
const uint8_t ADDRESS_LOCAL = 99;
const int ledPin = 13;
boolean packetComplete = false;
boolean packetStart = false;
uint8_t packetData[10] = { 0,0,0,0,0, 0,0,0,0,0 };
uint8_t packetPosition = 0;
uint8_t seq = 0;

void ledBlink();
void serial3SendPacket(const Packet& packet);
void serialDebugPacket(const Packet& packet);

void setup() {
	// Open serial communications and wait for port to open:
	Serial.begin(57600);
	while (!Serial) {
		; // wait for serial port to connect. Needed for native USB port only
	}

	pinMode(ledPin, OUTPUT);
	digitalWrite(ledPin, HIGH);
	delay(1000);
	digitalWrite(ledPin, LOW);
	Serial.print("Mega radio test - ADDRESS_LOCAL is ");
  Serial.println(ADDRESS_LOCAL, DEC);
	Serial3.begin(2400, SERIAL_8N1);
}

void loop() {

	ledBlink();
  /*
  Packet ping = Packet(ADDRESS_LOCAL, 186, PROTO_ICMP, OPT_NONE, 15, 0, 0);
  uint8_t pingData[1] = { ICMP_PING };
  ping.set_data(pingData);
  ping.set_chk(ping.calculate_checksum());
  serialDebugPacket(ping);
  serial3SendPacket(ping);
  return;
  */

	if (packetComplete) {
		//reset complete flag and store packetdata elsewhere in memory so it doesnt get changed? not sure how the serial recv works
		packetComplete = false;
		Packet packet = Packet(packetData);

		serialDebugPacket(packet);

		if (packet.is_checksum_valid() == false)
		{
      Serial.print("Ignoring packet with invalid checksum");
			return;
		}

		//Serial.print("destination = ");
		//Serial.println(packet.get_destination(), DEC);
		if (packet.get_destination() == 255 || packet.get_destination() == ADDRESS_LOCAL)
			//if (packet.is_relevant(ADDRESS_LOCAL))
		{
			Serial.println("packet is relevant to me");
      if (packet.get_opt() & OPT_ACK)
      {
        return; //dont reply to ACK
      }
     
			if (packet.get_proto() == PROTO_ICMP && packet.get_dlen() == 1 && packet.PacketData[5] == ICMP_PING)
			{
				Serial.println("Received ping packet to me, send pong");
				//TODO: actually send pong back
				Packet pongReply = Packet(ADDRESS_LOCAL, packet.get_source(), PROTO_ICMP, OPT_NONE, 15, packet.get_pid(), packet.get_seq());
				uint8_t pongData[1] = { ICMP_PONG };
				pongReply.set_data(pongData);
				pongReply.set_chk(pongReply.calculate_checksum()); //perhaps this should be elsewhere
				//serialDebugPacket(pongReply);
				serial3SendPacket(pongReply);
        return;
			}

      //default handling, send rst?
      //Packet reply = Packet(ADDRESS_LOCAL, packet.get_source(), packet.get_proto(), OPT_RST, 15, packet.get_pid(), packet.get_seq());
		}

	}

}

void ledBlink() {
	digitalWrite(ledPin, HIGH);
	delay(100);
	digitalWrite(ledPin, LOW);
}

void serial3SendPacket(const Packet& packet)
{
	uint8_t sendBuffer[17] = { PREAMBLE_BYTE, PREAMBLE_BYTE, PREAMBLE_BYTE, SOM_BYTE, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, EOM_BYTE, POSTAMBLE_BYTE, POSTAMBLE_BYTE };
	for (int i = 0; i < 10; ++i)
	{
		sendBuffer[4 + i] = packet.PacketData[i];
	}
	Serial3.write(sendBuffer, 17);
}

void serialEvent3() {
	while (Serial3.available()) {
		uint8_t inByte = Serial3.read();
		if (inByte == SOM_BYTE)
		{
			packetStart = true;
		}
		else if (packetStart == true)
		{
			if (inByte == EOM_BYTE)
			{
				packetStart = false;
				packetComplete = true;
				packetPosition = 0; //TODO: null terminate packet?
			}
			else {
				//put byte into buffer
				packetData[packetPosition] = inByte;
				packetPosition++;
			}
		}

	}
}

void serialDebugPacket(const Packet& packet)
{
    Serial.print("Packet content: ");
    for (int i = 0; i < 10; ++i)
    {
      Serial.print(packet.PacketData[i], DEC);
      Serial.print(" ");
    }
    Serial.println("");
}

