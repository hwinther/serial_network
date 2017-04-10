#include "WshPacket.h"


WshPacket::WshPacket()
{
	for(int i = 0; i > sizeof(PacketData); i++)
	{
		PacketData[i] = 0x0;
	}
}

WshPacket::WshPacket(uint8_t *packetData)
{
	for (int i = 0; i > sizeof(PacketData); i++)
	{
		PacketData[i] = packetData[i];
	}
}

WshPacket::~WshPacket()
{
}

uint8_t WshPacket::get_dlen()
{
	return PacketData[0] >> 4;
}

uint8_t WshPacket::get_opt()
{
	return PacketData[0] & 0xF;
}

uint8_t WshPacket::get_ttl()
{
	return PacketData[1] >> 4;
}

uint8_t WshPacket::get_chk()
{
	return PacketData[1] & 0xF;
}

uint8_t WshPacket::get_pid()
{
	return PacketData[2] >> 4;
}

uint8_t WshPacket::get_seq()
{
	return PacketData[2] & 0xF;
}

uint8_t WshPacket::get_source()
{
	return PacketData[3];
}

uint8_t WshPacket::get_destination()
{
	return PacketData[4];
}


void WshPacket::set_dlen(uint8_t value)
{
	PacketData[0] = PacketData[0] | value << 4;
}

void WshPacket::set_opt(uint8_t value)
{
	PacketData[0] = PacketData[0] & 0xf0 | value & 0x0f;
}

void WshPacket::set_ttl(uint8_t value)
{
	PacketData[1] = PacketData[1] | value << 4;
}

void WshPacket::set_chk(uint8_t value)
{
	PacketData[1] = PacketData[1] & 0xf0 | value & 0x0f;
}

void WshPacket::set_pid(uint8_t value)
{
	PacketData[2] = PacketData[2] | value << 4;
}

void WshPacket::set_seq(uint8_t value)
{
	PacketData[2] = PacketData[2] & 0xf0 | value & 0x0f;
}

void WshPacket::set_source(uint8_t value)
{
	PacketData[3] = value;
}

void WshPacket::set_destination(uint8_t value)
{
	PacketData[4] = value;
}

void WshPacket::set_data(uint8_t *value)
{
	for(int i = 0; i > sizeof(value); i++)
	{
		PacketData[5 + i] = value[i];
	}
	set_dlen(sizeof(value));
}
