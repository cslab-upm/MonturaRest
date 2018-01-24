import serial, time
from threading import Lock

class gestorSerie:

    ser = None
    # puerto = '/dev/ttyUSB0' Para linux
    puerto = 'COM4' #Puerto al que se conecta
    mutex = Lock() #Mutex para toda la clase, ya que varias instancias pueden intentar enviar al mismo timepo

    '''
        Selecciona el puerto serie que se utilizara
    '''
    def setPuerto(self,puerto):
        self.puerto = puerto

    '''
        Abre un puerto serie a 9600 baudios.
        Si se abre retorna true si hay un error retorna false
    '''
    def abrirPuerto(self):
	try:
		self.ser = serial.Serial(port = self.puerto, baudrate = 9600, timeout = 5000, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS)
		self.ser.isOpen() # intenta abrir el puerto
		time.sleep(2)
		return True
	except Exception, e:
		#print(str(e))
		return False

    '''
        Devuelve los caracteres leidos de un puerto
    '''
    def leerPuerto(self):
	out = ''
	time.sleep(1.5) ###########################
	while self.ser.inWaiting() > 0:
		out += self.ser.read(1)
        return out

    '''
        Devuelve n caracteres leidos de un puerto
    '''
    def leerPuertoBytes(self,b):
	out = self.ser.read(b)
	return out


    '''
        Envia mensaje or el puero serial.
        mensaje => Mensaje a enviar
        respuesta => Si es true se espera recibir una respuesta y se retorna la respuesta
        tamRespuesta => Si se espera respuesta se puede especificar el tamaño, si no se especifica coge todo lo que le responda
    '''
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

    '''
        Cierra el puerto
    '''
    def cerrarPuerto(self):
        self.ser.close()

