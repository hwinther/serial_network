' RECV PROXY FOR ARDUINO RX
#include "radionetwork.basinc"
setfreq m8

symbol TXPIN = 2
symbol TXSPEED = T2400_8
symbol RXPIN = 1
symbol RXSPEED = N2400_8
'symbol LOCAL_ADDRESS = 11
'#define LED
symbol LEDPIN = 4

'sertxd("recv proxy", 10, 13)
#ifdef LED
high LEDPIN
pause 1000
low LEDPIN
#endif

main:
	serin RXPIN, RXSPEED, (PREAMBLE, PREAMBLE, SOM), dlenopt, ttlchk, pidseq, src, dst, data0, data1, data2, data3, data4
	
	'sertxd ("got input: ")
	'sertxd (#dlenopt, " ", #ttlchk, " ", #pidseq, " ", #src, " ", #dst, " ", #data0, " ", #data1, " ", #data2, " ", #data3, " ", #data4, 10, 13)
	
	#ifdef LED
	high LEDPIN
	#endif

	gosub send
	
	#ifdef LED
	low LEDPIN
	#endif
goto main

send:
	' shouldn't need this when sending over serial to the connected device
	'for b11 = 0 to 9 ' 10
	'	serout TXPIN, TXSPEED, (POLYNOMINAL)
	'next b11
	serout TXPIN, TXSPEED, (PREAMBLE, PREAMBLE, SOM, dlenopt, ttlchk, pidseq, src, dst, data0, data1, data2, data3, data4, EOM, POSTAMBLE, POSTAMBLE)
return
