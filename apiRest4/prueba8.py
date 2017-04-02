numstr = "-34:48:47"
numstr2 = numstr.split(':')

i = 0
numero = 0
signo = 0
for x in numstr2:
    if i == 0:
        numero = int(x)
        if numero < 0:
            signo = -1
        else:
            signo = 1
    else:
        numero = numero + signo*int(x)/60.0
    i = 1
print numero
