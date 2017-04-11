' RECV PROXY FOR ARDUINO RX
#include "radionetwork.basinc"
setfreq m8

symbol TXPIN = 2
symbol TXSPEED = T2400_8
symbol RXPIN = 1
symbol RXSPEED = N2400_8
'symbol LOCAL_ADDRESS = 11
symbol LEDPIN = 4

'sertxd("recv proxy", 10, 13)
'high LEDPIN
'pause 1000
'low LEDPIN

main:
	serin RXPIN, RXSPEED, (PREAMBLE, PREAMBLE, SOM), dlenopt, ttlchk, pidseq, src, dst, data0, data1, data2, data3, data4
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
