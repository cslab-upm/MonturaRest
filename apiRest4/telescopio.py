import pycurl, json
import os, serial, time
from StringIO import StringIO
from threading import Thread, Lock

mutex = Lock()


def abrirPuerto(puerto):
	try:
		ser = serial.Serial(port = puerto, baudrate = 9600, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS)
		ser.isOpen()
		time.sleep(2)
		return ser
	except Exception, e:
		print(str(e))
		print('No se ha podido abrir el puerto '+puerto+'\r\n')
		exit()

def leerPuerto():
	out = ''
	time.sleep(2)
	while ser.inWaiting() > 0:
		out += ser.read(1)
        return out

def leerPuertoBytes(b):
	out = ser.read(b)
	return out

def modificarTarea(task, c):
	c.setopt(c.CUSTOMREQUEST, 'PUT')
	c.setopt(c.URL, '127.0.0.1:5000/api/mount/montegancedo/tasks/' + str(task['task']['id'])
	c.setopt(c.POSTFIELDS, json.dumps(task))
	c.perform()

def comunicacionTelescopio(task, c):
	mensaje = ""
	if task['title'] == 'movement':
		if task['type'] == 'time':
			dir = task['dir']
			time = task['timer']
			mensaje = ":Mg%s%s#" % (dir, time)
			mutex.acquire()
			ser.write(mensaje)
			mutex.release()

		elif task['type'] == 'coordinates':
			if task['mode'] == 'az-alt':
				print("aaaaaaa")
				g, m, s = task['alt'].split(':')
				mensaje = ":Sa%s*%s'%s#" % (g,m,s)
				mutex.acquire()
				ser.write(mensaje)
				respuesta = leerPuerto()
				print("La respuesta es: " +respuesta)
				mutex.release()

				if respuesta != '1':
					print("Error")
					task['done'] = True
					task['result'] = 'Error al establecer las coordenadas de altitud'
					modificarTarea(task, c)
					return
			
				g, m = task['az'].split(':')
				mensaje = ":Sz%s*%s#" % (g,m)
				mutex.acquire()
				ser.write(mensaje)
				respuesta = leerPuerto()
				mutex.release()

				if respuesta != '1':
					task['done'] = True
					task['result'] = 'Error al establecer las coordenadas de azimut'
					modificarTarea(task, c)
					return

				mensaje = ':MA#'
				mutex.acquire()
				ser.write(mensaje)	
				respuesta = leerPuerto()
				mutex.release()

				if respuesta != '0':
					task['done'] = True
					task['result'] = 'Error al desplazarse. ' + respuesta[1:-1]
					modificarTarea(task, c)
					return

			elif task['mode'] == 'RA-dec':
				h, m = task['RA'].split(':')
				mensaje = ":Sr%s*%s#" % (h,m)
				mutex.acquire()
				ser.write(mensaje)
				respuesta = leerPuerto()
				mutex.release()
				
				if respuesta != '1':
					task['done'] = True
					task['result'] = 'Error al establecer las coordenadas de ascension recta'
					modificarTarea(task, c)
					return
	
				g, m = task['dec'].split(':')
				mensaje = ":Sd%s*%s#" % (g,m)
				mutex.acquire()
				ser.write(mensaje)
				respuesta = leerPuerto()
				mutex.release()
				if respuesta != '1':
					task['done'] = True
					task['result'] = 'Error al establecer las coordenadas de declinacion'
					modificarTarea(task, c)
					return
				
				mensaje = ':MS#'
				mutex.acquire()
				ser.write(mensaje)	
				respuesta = leerPuerto()
				mutex.release()

				if respuesta != '0':
					task['done'] = True
					task['result'] = 'Error al desplazarse. ' + respuesta[1:-1]
					modificarTarea(task, c)
					return
	task['done'] = True
	task['result'] = 'Sin incidencias'

	modificarTarea(task, c)
	return

def getPosicion():
	url2 = '127.0.0.1:5000/api/mount/montegancedo/posicion'
	buf2 = StringIO()
	c2 = pycurl.Curl()
	c2.setopt(pycurl.USERPWD, "%s:%s" % ('montura', 'meade'))
	c2.setopt(c2.CUSTOMREQUEST, 'POST')
	c2.setopt(c2.HTTPHEADER, ['Content-Type: application/json'])
        c2.setopt(pycurl.DNS_SERVERS, '192.168.0.1')
	c2.setopt(c2.URL, url2)
	c2.setopt(c2.WRITEFUNCTION, buf2.write)


	while True:
		#altitud
		mutex.acquire()
		ser.write(":GA#")
		altitud = leerPuerto()
		mutex.release()
		
		#declinacion
		mutex.acquire()
		ser.write(":GD#")
		declinacion = leerPuerto()
		mutex.release()
		
		#RA
		mutex.acquire()
		ser.write(":GR#")
		RA = leerPuerto()
		mutex.release()
		
		#azimut
		mutex.acquire()
		ser.write(":GZ#")
		azimut = leerPuerto()
		mutex.release()
		
		# Devuelve sDD*MM:SS# pero detecta el * como simbolo desconocido
		#altitud = altitud[:-1].replace("'", ":").replace("*", ":")#.split("*") 
		altitud = altitud[0:3]+":"+altitud[4:-1]	

		# Devuelve sDD*MM:SS#
		#declinacion = declinacion[:-1].replace("'", ":").replace("*", ":")#.replace("'", "*").split("*")
		declinacion = declinacion[0:3]+":"+declinacion[4:-1]

		# Devuelve HH:MM:SS#
		RA = RA[:-1]#.split(":")
	
		# Devuelve DDD*MM:SS#
		#azimut = azimut[:-1].replace("'", ":").replace("*", ":")#.replace("'", "*").split("*")
		azimut = azimut[0:3]+":"+azimut[4:-1]

		data = json.dumps({'altitud': altitud, 'declinacion':declinacion, 'RA':RA, 'azimut':azimut})

		c2.setopt(c2.POSTFIELDS, data)
		c2.perform()
		time.sleep(10)


os.system("cls")
print('Introduce el puerto que deseas abrir, por ejemplo "/dev/ttyACM0"\r\n')
puerto = raw_input(">> ")
ser = abrirPuerto(puerto)
print('Puerto abierto')

t = Thread(target = getPosicion)
t.daemon = True
t.start()

c = pycurl.Curl()
c.setopt(pycurl.USERPWD, "%s:%s" % ('montura', 'meade'))
c.setopt(c.HTTPHEADER, ['Content-Type: application/json'])
c.setopt(pycurl.DNS_SERVERS, '192.168.0.1')

while True:
	url = '127.0.0.1:5000/api/mount/montegancedo/tasks?done=false'
	buf = StringIO()
	c.setopt(c.URL, url)
	c.setopt(c.CUSTOMREQUEST, 'GET')
	c.setopt(c.WRITEFUNCTION, buf.write)
	c.perform()

	buf1 = buf.getvalue()	
	
	try:
		tasks = json.loads(buf1)
	except Exception, e:
		time.sleep(5)
		continue

	for i in range(0,len(tasks['tasks'])):
		#print tasks['tasks'][i]['uri']
		comunicacionTelescopio(tasks['tasks'][i], c)
		time.sleep(2)
	time.sleep(5)
	buf.close()


