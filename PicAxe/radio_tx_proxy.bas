' SEND PROXY FOR ARDUINO TX
#include "radionetwork.basinc"
setfreq m8

symbol TXPIN = 2
symbol TXSPEED = N2400_8
symbol RXPIN = 1
symbol RXSPEED = T2400_8
'symbol LOCAL_ADDRESS = 11
symbol LEDPIN = 4

'sertxd("send proxy", 10, 13)
'high LEDPIN
'pause 500
'low LEDPIN
'pause 500
'high LEDPIN
'pause 500
'low LEDPIN

main:
	serin RXPIN, RXSPEED, (PREAMBLE, SOM), dlenopt, ttlchk, pidseq, src, dst, data0, data1, data2, data3, data4
	'sertxd ("got input: ")
	'sertxd (#dlenopt, " ", #ttlchk, " ", #pidseq, " ", #src, " ", #dst, " ", #data0, " ", #data1, " ", #data2, " ", #data3, " ", #data4, 10, 13)
	
	'high LEDPIN
	gosub send
	'low LEDPIN
goto main

send:
	for b11 = 0 to 9 ' 10
		serout TXPIN, TXSPEED, (POLYNOMINAL)
	next b11
	serout TXPIN, TXSPEED, (PREAMBLE, PREAMBLE, SOM, dlenopt, ttlchk, pidseq, src, dst, data0, data1, data2, data3, data4, EOM, POSTAMBLE, POSTAMBLE)
return
