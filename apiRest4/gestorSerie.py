import serial, time
from threading import Lock

class gestorSerie:

    ser = None
    # puerto = '/dev/ttyUSB0' Para linux
    puerto = 'COM4'
    mutex = Lock()

    def setPuerto(self,puerto):
        self.puerto = puerto

    def abrirPuerto(self):
	try:
		self.ser = serial.Serial(port = self.puerto, baudrate = 9600, timeout = 5000, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS)
		self.ser.isOpen() # intenta abrir el puerto
		time.sleep(2)
		return True
	except Exception, e:
		#print(str(e))
		return False

    def leerPuerto(self):
	out = ''
	time.sleep(1.5) ###########################
	while self.ser.inWaiting() > 0:
		out += self.ser.read(1)
        return out

    def leerPuertoBytes(self,b):
	out = self.ser.read(b)
	return out


    def enviar(self,mensaje, respuesta = False, tamRespuesta = 0):
        self.mutex.acquire()
        self.ser.write(mensaje)
        resp = None
        if (respuesta == True):
            resp = ''
            if (tamRespuesta == 0):
                resp = self.leerPuerto()
            else:
                resp = self.leerPuertoBytes(tamRespuesta)
        else:
            time.sleep(1.5) ############################################
        self.mutex.release()
        return resp


    def cerrarPuerto(self):
        self.ser.close()

