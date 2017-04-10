#pragma once
#include <stdint.h>
class WshPacket
{

public:
	WshPacket();
	WshPacket(uint8_t *packetData);
	~WshPacket();

	uint8_t PacketData[10];

	uint8_t get_dlen();
	uint8_t get_opt();
	uint8_t get_ttl();
	uint8_t get_chk();
	uint8_t get_pid();
	uint8_t get_seq();
	uint8_t get_source();
	uint8_t get_destination();

	void set_dlen(uint8_t value);
	void set_opt(uint8_t value);
	void set_ttl(uint8_t value);
	void set_chk(uint8_t value);
	void set_pid(uint8_t value);
	void set_seq(uint8_t value);
	void set_source(uint8_t value);
	void set_destination(uint8_t value);

	void WshPacket::set_data(uint8_t *value);
};
