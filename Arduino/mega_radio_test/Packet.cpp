#include "Packet.h"

Packet::Packet()
{
}

Packet::Packet(uint8_t *packetData)
{
	//sizeof(packetData)
	for (int i = 0; i < 10; ++i)
	{
		PacketData[i] = packetData[i];
	}
}

Packet::Packet(uint8_t source, uint8_t destination, uint8_t proto, uint8_t opt, uint8_t ttl, uint8_t pid, uint8_t seq)
{
	set_source(source);
	set_destination(destination);
	set_proto(proto);
	set_opt(opt);
	set_ttl(ttl);
	set_pid(pid);
	set_seq(seq);
}

Packet::~Packet()
{
}

uint8_t Packet::get_dlen()
{
	return PacketData[0] >> 5;
}

uint8_t Packet::get_proto()
{
	return (PacketData[0] & 0x1C) >> 2;
}

uint8_t Packet::get_opt()
{
	return PacketData[0] & 0x3;
}

uint8_t Packet::get_ttl()
{
	return PacketData[1] >> 4;
}

uint8_t Packet::get_chk()
{
	return PacketData[1] & 0xF;
}

uint8_t Packet::get_pid()
{
	return PacketData[2] >> 4;
}

uint8_t Packet::get_seq()
{
	return PacketData[2] & 0xF;
}

uint8_t Packet::get_source()
{
	return PacketData[3];
}

uint8_t Packet::get_destination()
{
	return PacketData[4];
}


void Packet::set_dlen(uint8_t value)
{
	PacketData[0] = PacketData[0] | value << 5;
}

void Packet::set_proto(uint8_t value)
{
	//assign        set relevant bits to 0  bitshift      remove bits outside of range
	PacketData[0] = PacketData[0] & 0xE3 | value << 2 & 0x1C;
}

void Packet::set_opt(uint8_t value)
{
	PacketData[0] = PacketData[0] & 0xFC | value & 0x3;
}

void Packet::set_ttl(uint8_t value)
{
	PacketData[1] = PacketData[1] | value << 4;
}

void Packet::set_chk(uint8_t value)
{
	PacketData[1] = PacketData[1] & 0xf0 | value & 0x0f;
}

void Packet::set_pid(uint8_t value)
{
	PacketData[2] = PacketData[2] | value << 4;
}

void Packet::set_seq(uint8_t value)
{
	PacketData[2] = PacketData[2] & 0xf0 | value & 0x0f;
}

void Packet::set_source(uint8_t value)
{
	PacketData[3] = value;
}

void Packet::set_destination(uint8_t value)
{
	PacketData[4] = value;
}

void Packet::set_data(uint8_t *value)
{
	int s = sizeof(value);
	if (s == 0)
	{
		set_dlen(0);
		return;
	}

	for (int i = 0; i < s; ++i)
	{
		PacketData[5 + i] = value[i];
	}
	set_dlen(s - 1);
}

uint8_t Packet::calculate_checksum()
{
	uint8_t checksum = 0;
	for (int i = 0; i < 10; ++i)
	{
		checksum ^= PacketData[i] >> 4; //hnibble
			// we have to skip the checksum itself when creating a checksum, duh
		if (i != 1)
		{
			checksum ^= PacketData[i] & 0xF; //lnibble
		}
	}
	return checksum;
}

//various boolean helper methods
bool Packet::is_broadcast()
{
	return PacketData[4] == ADDRESS_BROADCAST;
}

bool Packet::is_relevant(uint8_t address_local)
{
	return PacketData[4] == address_local || PacketData[4] == ADDRESS_BROADCAST;
}

bool Packet::is_checksum_valid()
{
	return calculate_checksum() == get_chk();
}
