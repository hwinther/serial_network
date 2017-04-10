' TEST RECEIVING UNIT WITH BLINKING LED, YO

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


high LEDPIN
pause 500
sertxd("blinking recv", 10, 13)
low LEDPIN

main:
	'serin RXPIN, RXSPEED, b0, b1, b2, b3
	'sertxd ("i: ")
	'sertxd (#b0, 32, #b1, 32, #b2, 32, #b3, 10, 13)
	'goto main
	
	serin RXPIN, RXSPEED, (PREAMBLE, SOM), dlenopt, ttlchk, pidseq, src, dst, data0, data1, data2, data3, data4
	high LEDPIN
	sertxd (":", #data4, 10, 13)
	'sertxd (#dlenopt, " ", #ttlchk, " ", #pidseq, " ", #src, " ", #dst, " ", #data0, " ", #data1, " ", #data2, " ", #data3, " ", #data4, 10, 13)
	low LEDPIN

goto main
