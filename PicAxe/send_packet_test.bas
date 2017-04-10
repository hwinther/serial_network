' radio send packet test
setfreq m8

symbol TXPIN = 2
symbol TXSPEED = N2400_8
symbol RXPIN = 1
symbol RXSPEED = N2400_8
'symbol LOCAL_ADDRESS = 11
symbol LEDPIN = 4

symbol PREAMBLE = 0xAA
symbol SOM = 0xC5
symbol EOM = 0x5C
symbol POSTAMBLE = 0x3A
symbol POLYNOMINAL = 0x8C
symbol dlenopt = b0
symbol ttlchk = b1
symbol pidseq = b2
symbol src = b3
symbol dst = b4
symbol data0 = b5
symbol data1 = b6
symbol data2 = b7
symbol data3 = b8
symbol data4 = b9

symbol PROTO_RAW = 0x0
symbol PROTO_ICMP = 0x1
symbol PROTO_RES1 = 0x2
symbol PROTO_RES2 = 0x4
symbol OPT_FORWARD = 0x8
symbol ICMP_PING = 0x0
symbol ICMP_PONG = 0x1

dlenopt = 10
ttlchk = 9
pidseq = 8
src = 7
dst = 6
data0 = 5
data1 = 4
data2 = 3
data3 = 2
data4 = 1

main:

	for b11 = 0 to 9 ' 10
		serout TXPIN, TXSPEED, (POLYNOMINAL)
	next b11

	serout TXPIN, TXSPEED, (PREAMBLE, PREAMBLE, SOM, dlenopt, ttlchk, pidseq, src, dst, data0, data1, data2, data3, data4, EOM, POSTAMBLE, POSTAMBLE)

	pause 3000
	
goto main
