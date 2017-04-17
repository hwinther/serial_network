' TEST RECEIVING UNIT WITH BLINKING LED, YO
#include "radionetwork.basinc"
setfreq m8

'symbol TXPIN = 2
'symbol TXSPEED = N2400_8
symbol RXPIN = 1
symbol RXSPEED = N2400_8
'symbol LOCAL_ADDRESS = 11
symbol LEDPIN = 4

high LEDPIN
pause 500
sertxd("blinking recv", 10, 13)
low LEDPIN

main:
	'serin RXPIN, RXSPEED, b0, b1, b2, b3
	'sertxd ("i: ", #b0, 32, #b1, 32, #b2, 32, #b3, 10, 13)
	'goto main
	
	serin RXPIN, RXSPEED, (PREAMBLE, SOM), dlenopt, ttlchk, pidseq, src, dst, data0, data1, data2, data3, data4
	high LEDPIN
	'sertxd (":", #data4, 10, 13)
	sertxd (#dlenopt, " ", #ttlchk, " ", #pidseq, " ", #src, " ", #dst, " ", #data0, " ", #data1, " ", #data2, " ", #data3, " ", #data4, 10, 13)
	low LEDPIN

goto main
