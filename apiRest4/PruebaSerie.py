from gestorSerie import gestorSerie
s = gestorSerie()

s.setPuerto('COM1')
if (s.abrirPuerto() == False):
    print('No se ha podido abrir el puerto '+s.puerto)
    print('Introduce un puerto a abrir')
    puerto = raw_input('>> ')
    s.setPuerto(puerto)
    if (s.abrirPuerto() == False):
        print('No se ha podido abrir el puerto '+s.puerto)
        exit()
print('Puerto abierto correctamente')
print(s.ser)

print ('Introduce el mensaje a enviar')
msj = raw_input('>> ')
respuesta = s.enviar(msj)
print (respuesta)
s.cerrarPuerto()
