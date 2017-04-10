//#include <xstddef>
const uint8_t PREAMBLE_BYTE = 0xAA; //170
const uint8_t SOM_BYTE = 0xC5; //197
const uint8_t EOM_BYTE = 0x5C; //92
const uint8_t POSTAMBLE_BYTE = 0x3A; //58
const uint8_t POLYNOMIAL = 0x8C; //140

const uint8_t PROTO_RAW = 0x0;
const uint8_t PROTO_ICMP = 0x1;
const uint8_t PROTO_RES1 = 0x2;
const uint8_t PROTO_RES2 = 0x4;
const uint8_t OPT_FORWARD = 0x8;
const uint8_t ICMP_PING = 0x0;
const uint8_t ICMP_PONG = 0x1;

const uint8_t LOCAL_ADDRESS = 99;

const int ledPin = 13;

uint8_t incomingByte = 0;   // for incoming serial data

boolean packetComplete = false;
boolean packetStart = false;
uint8_t packetData[10] = { 0,0,0,0,0, 0,0,0,0,0 };
uint8_t packetPosition = 0;
uint8_t seq = 0;

void ledBlink();

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
	Serial.println("Mega radio test init");
	Serial3.begin(2400, SERIAL_8N1);
}

void loop() {

	ledBlink();

	/*
	byte msg[17] = { PREAMBLE_BYTE, PREAMBLE_BYTE, PREAMBLE_BYTE, SOM_BYTE, 1, 2, 3, 4, 5, 6, 7, 8, 9, seq, EOM_BYTE, POSTAMBLE_BYTE, POSTAMBLE_BYTE };
	Serial3.write(msg, 17);
	delay(2000);
	seq++;
	if (seq == 255)
	{
		seq = 0;
	}
	*/

	if (packetComplete) {
		Serial.print("received packet: ");
		for (int i = 0; i < 10; i++)
		{
			Serial.print(packetData[i], DEC);
			Serial.print(" ");
		}
		Serial.println("");

		uint8_t dlenopt = packetData[0];
		uint8_t	ttlchk = packetData[1];
		uint8_t	pidseq = packetData[2];

		uint8_t dataLength = dlenopt >> 4;
		uint8_t options = dlenopt & 0xF;

		uint8_t timeToLive = ttlchk >> 4;
		uint8_t checksum = ttlchk & 0xF;

		uint8_t id = pidseq >> 4;
		uint8_t sequence = pidseq & 0xF;

		uint8_t source = packetData[3];
		uint8_t destination = packetData[4];

		uint8_t data[5] = { 0,0,0,0,0 };
		if (dataLength != 0 && dataLength < 5)
		{
			for (int i = 0; i < dataLength; i++)
			{
				data[i] = packetData[5 + i];
			}
		}

		//TODO: checksum validation

		if (destination == 255 || destination == LOCAL_ADDRESS)
		{
			if (options & PROTO_ICMP && dataLength == 1 && data[0] == ICMP_PING)
			{
				Serial.println("Received ping packet to me, send pong");
				//TODO: actually send pong back
				dataLength = 1;
				data[0] = ICMP_PONG;
				options = PROTO_ICMP;
				dlenopt = dataLength * 16 + options;

				timeToLive = 15;
				checksum = 0;
				ttlchk = timeToLive * 16 + checksum;

				id = 0;
				sequence = 0;
				pidseq = id * 16 + sequence;

				destination = source;
				source = LOCAL_ADDRESS;

				uint8_t newPacketData[10] = {dlenopt, ttlchk, pidseq, destination, source};
				for(int i = 0; i > dataLength; i++)
				{
					newPacketData[5 + i] = data[i];
				}
				for (int i = 0; i > 5 + dataLength; i++)
				{
					uint8_t first = newPacketData[i] >> 4;
					uint8_t last = newPacketData[i] & 0xF;
					// we have to skip the checksum itself when creating a checksum, duh
					if (i != 0)
					{
						checksum ^= first;
					}
					checksum ^= last;
				}
				ttlchk = timeToLive * 16 + checksum;

				byte msg[13] = { PREAMBLE_BYTE, PREAMBLE_BYTE, PREAMBLE_BYTE, SOM_BYTE, dlenopt, ttlchk, pidseq, source, destination, data[0], EOM_BYTE, POSTAMBLE_BYTE, POSTAMBLE_BYTE };
				Serial3.write(msg, 13);
			}
		}

   packetComplete = false;
	}

}

void ledBlink() {
	digitalWrite(ledPin, HIGH);
	delay(100);
	digitalWrite(ledPin, LOW);
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
