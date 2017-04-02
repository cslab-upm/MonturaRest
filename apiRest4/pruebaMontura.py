from montura import montura
from gestorMontura import gestorMontura
import time, json

'''peticion = json.dumps({'id':1,'orden':{'title': 'movement', 'type': 'time', 'timer': 1000,'dir':'s'}})
m = montura()

m.procesarPeticion(peticion)

time.sleep(2)
peticion = json.dumps({'id':2,'orden':{'title': 'movement', 'type': 'coordinates', 'mode': 'RA-dec', 'coordenadas': {'RA': '99:90', 'dec': '88:80'}}})
m.procesarPeticion(peticion)

time.sleep(2) # Necesita tiempo para recibir mensajes

peticion = json.dumps({'id':3,'orden':{'title': 'movement', 'type': 'coordinates', 'mode': 'az-alt', 'coordenadas': {'az': '333:30', 'alt': '+20:10:20'}}})
m.procesarPeticion(peticion)
                      
time.sleep(2)
print(m.getRA()) # Aparentemente aqui necesita menos tiempo
time.sleep(1)
print(m.getDec())
time.sleep(1)
print(m.getAlt())
time.sleep(1)
print(m.getAz())
'''
#m = montura()
#print(m.setSeguimiento(True))
'''print(m.setSeguimiento(True))
print(m.setSeguimiento(False))
print(m.setSeguimiento(True))
time.sleep(5)
print(m.setSeguimiento(True))'''
#time.sleep(2)
#peticion = json.dumps({'id':1,'orden':{'title': 'movement', 'type': 'time', 'timer': 1000,'dir':'s'}})
#m.procesarPeticion(peticion)
#for p in m.posiciones.all():
#    print p

m= gestorMontura()

peticion = json.dumps({'id':1,'orden':{'title': 'seguimiento', 'type': 'intervalo', 'intervalo': 10}})
m.procesarPeticion(peticion)

peticion = json.dumps({'id':1,'orden':{'title': 'seguimiento', 'type': 'estado', 'activo': True}})
m.procesarPeticion(peticion)

time.sleep(20)
peticion = json.dumps({'id':1,'orden':{'title': 'seguimiento', 'type': 'estado','activo': False}})
m.procesarPeticion(peticion)

print(m.getStatus())
print('Finalizado')
