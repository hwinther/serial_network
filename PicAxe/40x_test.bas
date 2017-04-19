' radio infinite recv test
#include "radionetwork.basinc"

SYMBOL TX_PIN = B.4
SYMBOL TX_SPEED = N2400_4
SYMBOL RX_PIN = A.1
SYMBOL RX_SPEED = N2400_4
SYMBOL LED_PIN = B.0


init:
	high LED_PIN
	pause 1000
	low LED_PIN
	'setfreq m4
	'serout TX_PIN, T2400_4, ("aaaa")
	sertxd("init",10,13)

main:
	high LED_PIN
	gosub senddata
	'serin 3, T2400_4, (97,97,97), b0, b1, b2
	'serin RX_PIN, RX_SPEED, (PREAMBLE, SOM), dlenopt, ttlchk, pidseq, src, dst, data0, data1, data2, data3, data4
	'serin RX_PIN, RX_SPEED, b0, b1, b2, b3, b4, b5
	'sertxd("i: ")
	'sertxd(#b0, 32, #b1, 32, #b2, 32, #b3, 32, #b4, 32, #b5, 10, 13)
	'debug b0
	'debug b1
	'debug b2
	'high LED_PIN
	'pause 1000
	
	pause 2000
	low LED_PIN

	goto main


senddata:
	for b0 = 0 to 5
		serout TX_PIN, TX_SPEED, (POLYNOMINAL)
	next
	serout TX_PIN, TX_SPEED, (PREAMBLE, PREAMBLE, SOM, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, EOM, POSTAMBLE, POSTAMBLE)

	return
