#pragma once

#include <stdint.h>
const uint8_t PREAMBLE_BYTE = 0xAA; //170
const uint8_t SOM_BYTE = 0xC5; //197
const uint8_t EOM_BYTE = 0x5C; //92
const uint8_t POSTAMBLE_BYTE = 0x3A; //58
const uint8_t POLYNOMIAL = 0x8C; //140

const uint8_t PROTO_RAW = 0x0;
const uint8_t PROTO_ICMP = 0x1;
const uint8_t PROTO_ACKREQ = 0x2;
const uint8_t PROTO_SYN = 0x3;
const uint8_t PROTO_SYNACK = 0x4;
const uint8_t PROTO_FIN = 0x5;
const uint8_t PROTO_FINACK = 0x6;
const uint8_t PROTO_RES1 = 0x7;

const uint8_t OPT_NONE = 0x0;
const uint8_t OPT_ACK = 0x1;
const uint8_t OPT_RST = 0x2;

const uint8_t ICMP_PING = 0x0;
const uint8_t ICMP_PONG = 0x1;

const uint8_t ADDRESS_NETWORKIDENTIFIER = 0;
const uint8_t ADDRESS_BROADCAST = 255;

//enum Address {
//	IDENTIFIER = 0,
//	BROADCAST = 255
//};
