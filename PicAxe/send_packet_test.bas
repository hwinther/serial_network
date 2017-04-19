' radio send packet test
#include "radionetwork.basinc"

'setfreq m8

symbol TXPIN = 2
symbol TXSPEED = N2400_8
symbol RXPIN = 1
symbol RXSPEED = N2400_8
'symbol LOCAL_ADDRESS = 11
symbol LEDPIN = 4

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
