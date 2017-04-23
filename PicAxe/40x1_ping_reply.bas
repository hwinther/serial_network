' picaxe ping reply
#include "radionetwork.basinc"

setfreq m8

SYMBOL TX_PIN = B.4
SYMBOL TX_SPEED = N2400_8

SYMBOL RX_PIN = 0 ' A.1
SYMBOL RX_SPEED = N2400_8

SYMBOL LED_PIN = B.0

SYMBOL ADDRESS_LOCAL = 240

init:
	high LED_PIN
	pause 1000
	low LED_PIN
	sertxd("picaxe ping reply, ADDRESS_LOCAL is ", #ADDRESS_LOCAL, 10, 13)

main:
	serin RX_PIN, RX_SPEED, (PREAMBLE, SOM), dlenopt, ttlchk, pidseq, src, dst, data0, data1, data2, data3, data4
	
	high LED_PIN
	
	' sertxd (#dlenopt, " ", #ttlchk, " ", #pidseq, " ", #src, " ", #dst, " ", #data0, " ", #data1, " ", #data2, " ", #data3, " ", #data4, 10, 13)
	
	if dst = ADDRESS_LOCAL then gosub relevant_packet

	low LED_PIN

	goto main
	
relevant_packet:
	' sertxd ("packet relevant to me", 10, 13)
	' 000 000 00
	' dl  pro opt
	'sertxd("dlenopt=", #dlenopt, 10, 13)
	b10 = dlenopt / 32 ' datalength
	b11 = dlenopt & %00011100 ' protocol
	b11 = b11 >> 2
	if b11 = PROTO_ICMP and b10 = 1 and data0 = ICMP_PING then
		'sertxd ("rp", 10, 13)
		data0 = ICMP_PONG
		' we will flip sender/recv (if this is broadcast, then chk will fail!)
		' and reuse the rest minus data0 - thus we only need to add 1 to chk
		'sertxd("0=", #ttlchk, 10, 13)
		b10 = ttlchk & %00001111 ' get only chk
		'sertxd("1=", #b10, 10, 13)
		b10 = b10 ^ ICMP_PONG
		'sertxd("2=", #b10, 10, 13)
		ttlchk = ttlchk & %11110000 ' remove chk
		'sertxd("3=", #ttlchk, 10, 13)
		ttlchk = ttlchk | b10 ' set chk
		'sertxd("4=", #ttlchk, 10, 13)
		pause 500 ' 0.5s gracetime (in case our reply overlaps with POSTAMBLES from the received packet)
		gosub send_reply
	endif
return
	
send_reply:
	dst = src
	src = ADDRESS_LOCAL

senddata:
	for b11 = 0 to 4 ' 5
		serout TX_PIN, TX_SPEED, (POLYNOMINAL)
	next
		serout TX_PIN, TX_SPEED, (PREAMBLE, PREAMBLE, SOM, dlenopt, ttlchk, pidseq, src, dst, data0, data1, data2, data3, data4, EOM, POSTAMBLE, POSTAMBLE)

	return
