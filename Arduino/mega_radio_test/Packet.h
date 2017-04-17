#pragma once
#include <stdint.h>
#include "Protocol.h"

class Packet
{

public:
	Packet();
	Packet(uint8_t *packetData);
	Packet(uint8_t source, uint8_t destination, uint8_t proto = 0, uint8_t opt = 0, uint8_t ttl = 0, uint8_t pid = 0, uint8_t seq = 0);
	~Packet();

	uint8_t PacketData[10]= {0,0,0,0,0, 0,0,0,0,0};

	uint8_t get_dlen();
	uint8_t get_proto();
	uint8_t get_opt();
	uint8_t get_ttl();
	uint8_t get_chk();
	uint8_t get_pid();
	uint8_t get_seq();
	uint8_t get_source();
	uint8_t get_destination();

	void set_dlen(uint8_t value);
	void set_proto(uint8_t value);
	void set_opt(uint8_t value);
	void set_ttl(uint8_t value);
	void set_chk(uint8_t value);
	void set_pid(uint8_t value);
	void set_seq(uint8_t value);
	void set_source(uint8_t value);
	void set_destination(uint8_t value);

	void set_data(uint8_t *value);

	uint8_t calculate_checksum();

	bool is_broadcast();
	bool is_relevant(uint8_t address_local);
	bool is_checksum_valid();
};
