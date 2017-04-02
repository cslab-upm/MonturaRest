import pycurl, json
import os, time
from StringIO import StringIO

def resultado(c,buf1):
	
	task = {}
	try:
		task = json.loads(buf1)
	except Exception, e:
		print 'Error en la peticion\n'
		print e
		return
	print '\nPeticion enviada. Esperando respuesta...'
	
	url = '127.0.0.1:5000/api/mount/montegancedo/tasks/' + str(task['task']['id'])
	c.setopt(c.CUSTOMREQUEST, 'GET')
	c.setopt(c.URL, url)

	while(task['task']['done'] == False):

		buf = StringIO()
		c.setopt(c.WRITEFUNCTION, buf.write)
		c.perform()
		buf1 = buf.getvalue()
		buf.close()
		task = json.loads(buf1)
		time.sleep(2) 

	print '\nTarea ejecutada. Resultado:\n' +task['task']['result']
	raw_input("\nPresiona enter para continuar...")
	return

def imprimirPosicion(c):
	'''url = '127.0.0.1:5000/api/mount/montegancedo/posicion'
	buf = StringIO()

	c.setopt(c.CUSTOMREQUEST, 'GET')
	c.setopt(c.URL, url)
	c.setopt(pycurl.USERPWD, "%s:%s" % ('montura', 'meade'))
	c.setopt(c.HTTPHEADER, ['Content-Type: application/json'])
	c.setopt(c.WRITEFUNCTION, buf.write)
	c.perform()

	buf1 = buf.getvalue()
	buf.close()

	try:
		posicion = json.loads(buf1)
	except Exception, e:
		print 'No hay datos de posicion\n'
		return

	print 'Altitud: %s                   Azimut: %s' % (posicion['posicion']['altitud'], posicion['posicion']['azimut'])
	print 'Ascension recta: %s            Declinacion: %s\n' % (posicion['posicion']['RA'], posicion['posicion']['declinacion'])
	return
        '''
	pass

def menuMover(c):
	os.system("cls")
	imprimirPosicion(c)
	print('Seleccione el tipo de movimiento: \n 0) Salir\n 1) Mover por tiempo\n 2) Indicar coordenadas\n 3) Seguimiento\n')
	seleccion = raw_input(">> ")
	
	if seleccion == '0':
		print "Saliendo...\n"
		exit()

	elif seleccion == '1':
		menuMoverTiempo(c)
		return

	elif seleccion == '2':
		menuMoverCoordenadas(c)
		return

	elif seleccion == '3':
                menuSeguimiento(c)
                return

def menuMoverTiempo(c):
	os.system("cls")
	imprimirPosicion(c)
	print('Indique la direccion:\n 0) Volver\n 1) Norte\n 2) Sur\n 3) Este\n 4) Oeste\n')
	dir = 'n'
	seleccion = raw_input(">> ")
	
	if seleccion == '0':
		menuMover(c)
		return

	elif seleccion == '1':
		dir = 'n'
	elif seleccion == '2':
		dir = 's'
	elif seleccion == '3':
		dir = 'w' # Va hacia la derecha poniendo oeste...
	elif seleccion == '4':
		dir = 'e' # Va hacia la izquierda poniente este...

	print('\nIntroduce el tiempo en ms \r\n')
	tiempo = raw_input(">> ")

	while len(tiempo)<4:
		tiempo = '0'+tiempo

	if len(tiempo)>4:
		print "ERROR. El formato de tiempo debe ser 0000"
		time.sleep(3)
		menuMoverTiempo(c)
		return

	data = json.dumps({'orden':{'title': 'movement', 'type': 'time', 'timer': tiempo,'dir':dir}})
	buf = StringIO()
	c.setopt(c.CUSTOMREQUEST, 'POST')
	c.setopt(c.URL, url)
	c.setopt(c.WRITEFUNCTION, buf.write)
	c.setopt(c.POST, 1)
	c.setopt(c.POSTFIELDS, data)
	c.perform()
	print data
	buf1 = buf.getvalue()
	buf.close()
	
	#resultado(c, buf1)
	time.sleep(5)

	menuMoverTiempo(c)
	return

def menuMoverCoordenadas(c):
	os.system("cls")
	imprimirPosicion(c)
	print('Indique el tipo de coordenadas que desea emplear:\n 0) Volver\n 1) Altitud/Azimut\n 2) Declinacion/Ascension recta \n')
	seleccion = raw_input(">> ")
	data = {'orden': {'title': 'movement', 'type': 'coordinates'}}
	
	if seleccion == '0':
		menuMover(c)
		return
	
	elif seleccion == '1':	

		# sDD*MM'ss
		gAlt = raw_input("\nIntroduce los grados de altitud incluyendo el signo: ")
		mAlt = raw_input("Introduce los minutos de altitud: ")
		sAlt = raw_input("Introduce los segundos de altitud: ")
		
		altitud = gAlt+":"+mAlt+":"+sAlt
		
		# DDD*MM
		gAz = raw_input('\nIntroduce los grados de azimut: ')
		mAz = raw_input('Introduce los minutos de azimut: ')

		azimut = gAz+':'+mAz

		data['orden']['mode'] = 'az-alt'
		data['orden']['coordenadas'] = {'az': azimut, 'alt': altitud}
		
	elif seleccion == '2':
		
		# sDD*MM:SS
		gDec = raw_input('\nIntroduce los grados de declinacion con signo: ')
		mDec = raw_input('Introduce los minutos de declinacion: ')

		declinacion = gDec+':'+mDec
		
		# HH:MM:SS
		hRa = raw_input('\nIntroduce las horas de ascension recta: ')
		mRa = raw_input('Introduce los minutos de ascension recta: ')

		RA = hRa+':'+mRa

		data['orden']['mode'] = 'RA-dec'
		data['orden']['coordenadas'] = {'dec': declinacion, 'RA': RA}
	
	json_data = json.dumps(data)	
	buf = StringIO()
	url = '127.0.0.1:5000/api/mount/montegancedo/tasks'
	c.setopt(c.CUSTOMREQUEST, 'POST')
	c.setopt(c.URL, url)
	c.setopt(c.WRITEFUNCTION, buf.write)
	c.setopt(c.POST, 1)
	c.setopt(c.POSTFIELDS, json_data)
	c.perform()

	buf1 = buf.getvalue()
	buf.close()

	menuMoverCoordenadas(c)

def menuSeguimiento(c):
        os.system("cls")
	imprimirPosicion(c)
	print('Seleccione que hacer: \n 0) Volver\n 1) Activar\n 2) Desactivar\n 3) Intervalo\n')
	seleccion = raw_input(">> ")

	data = {}
	if seleccion == '0':
		menuMover(c)
		return

	elif seleccion == '1':
		data = {'orden': {'title': 'seguimiento', 'type': 'estado', 'activo': True}}

        elif seleccion == '2':
                data = {'orden': {'title': 'seguimiento', 'type': 'estado', 'activo': False}}
                
        elif seleccion == '3':
                print('Introduce el tiempo nuevo: ')
                resp = raw_input(' >> ')
                data = {'orden': {'title': 'seguimiento', 'type': 'intervalo', 'intervalo': resp}}

        json_data = json.dumps(data)
        print json_data
	buf = StringIO()
	url = '127.0.0.1:5000/api/mount/montegancedo/tasks'
	c.setopt(c.CUSTOMREQUEST, 'POST')
	c.setopt(c.URL, url)
	c.setopt(c.WRITEFUNCTION, buf.write)
	c.setopt(c.POST, 1)
	c.setopt(c.POSTFIELDS, json_data)
	c.perform()

	buf1 = buf.getvalue()
	buf.close()

	time.sleep(5)

	menuSeguimiento(c)


os.system("cls")
print 'Cliente iniciado'

buf = StringIO()
url = '127.0.0.1:5000/api/mount/montegancedo/posicion'

c = pycurl.Curl()
c.setopt(c.CUSTOMREQUEST, 'GET')
c.setopt(c.URL, url)
c.setopt(pycurl.USERPWD, "%s:%s" % ('montura', 'meade'))
c.setopt(pycurl.DNS_SERVERS, '192.168.1.1') # Necesario en windows
c.setopt(c.HTTPHEADER, ['Content-Type: application/json'])
c.setopt(c.WRITEFUNCTION, buf.write)
try:
	t = time.clock()
	c.perform()
	print("Tiempo que ha tardado: {} segundos".format(time.clock() - t))
	print 'Conexion establecida'
	time.sleep(2)
except Exception, e:
	print 'No se ha podido establecer la conexion\n'
	print e
	exit()

buf1 = buf.getvalue()
buf.close()


url = '127.0.0.1:5000/api/mount/montegancedo/tasks'
menuMover(c)

os.system("cls") # Windows -> cls, Linux -> clear



