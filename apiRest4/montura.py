from monturaGloria import monturaGloria
from tinydb import TinyDB, Query
from gestorSerie import gestorSerie as ser
from threading import Thread, Timer
import time, json
import gestorLoggings as gl
import rabbitmq_device as rmq 

class montura(monturaGloria):

    # Caracteristicas
    nombre = 'Montura'
    home = None
    permitirMovimiento = True
    cola = None
    sender = rmq.RabbitMQ_sender('montura', "192.168.1.5")

    # Posicion
    az = '+00:00:00'
    ra = '00:00:00'
    dec = '+00:00:00'
    alt = '000:00:00'

    # Seguimiento
    seguimiento = False
    tSeguimiento = 2 # segundos
    aceptarThread = True
    tSeguimientoMin = 2
    tSeguimientoMax = 30
    llegando = False
    llegandoModo = 'az-alt'
    llegandoPosicion = [0, 0]
    resultadoLlegando = 'Sin incidencias'

    # Serial
    serial = ser()
    '''
    # Base de datos
    db = TinyDB('database.json')
    tareas = db.table('tareas')
    posiciones = db.table('posiciones')
    q = Query()
    '''
    # ---------- Metodos ------------

    # Intentamos abrir un puerto por defecto. Si no, pedimos uno
    def iniciarSerie(self):
        # Pedimos puertos hasta que haya uno valido
        while (self.serial.abrirPuerto() == False):
            print('No se ha podido abrir el puerto '+self.serial.puerto)
            print('Introduce un puerto a abrir')
            puerto = raw_input('>> ')

            # Cierra el programa si se introduce exit como puerto
            if (puerto == 'exit'):
                print('Saliendo...')
                exit()

            self.serial.setPuerto(puerto)
        print('Puerto abierto: ' +self.serial.puerto)

    #Funcion comunica la posicion Azimut
    def comunicarAzimut(self):
        while True:
	    grados = self.getAz()[0:3]
            self.sender.send_message('info','D{}'.format(grados))
	    #print(grados)
            time.sleep(10)
	
    # Al instanciar iniciamos abriendo el puerto serie
    def __init__(self):
        print('Iniciando...')
        self.iniciarSerie()
        self.getRA()
        self.getDec()
        self.getAz()
        self.getAlt()
	thread = Thread(target = self.comunicarAzimut)
	thread.start()

    def setCola(self, cola):
        self.cola = cola

# --------------------------------------------------------------------

    # Estado actual del telescopio
    def getStatus(self):
        return [self.nombre, self.seguimiento, self.tSeguimiento, self.ra, self.dec, self.az, self.alt]

    # Devuelve el valor de la ascension recta
    def getRA(self):
        print('Devuelve la ascension recta')
        mensaje = ":GR#"
        # Devuelve HH:MM:SS#
        ra = self.getPosicion(mensaje)
        ra = ra[:-1]#.split(":")
        self.ra = ra
        return ra

    # Devuelve el valor de la declinacion
    def getDec(self):
        print('Devuelve la declinacion')
        mensaje = ":GD#"
        # Devuelve sDD*MM:SS#
        declinacion = self.getPosicion(mensaje)
        declinacion = declinacion[0:3]+":"+declinacion[4:-1]
        self.dec = declinacion
        return declinacion

    # Devuelve el valor de la altitud
    def getAlt(self):
        print('Devuelve la altitud')
        mensaje = ':GA#'
        # Devuelve sDD*MM:SS# pero detecta el * como simbolo desconocido
        altitud = self.getPosicion(mensaje)
	print(altitud)
        altitud = altitud[0:3]+":"+altitud[4:-1]
        self.alt = altitud
        return altitud

    # Devuelve el valor de azimut
    def getAz(self):
        #print('Devuelve el azimut')
        mensaje = ':GZ#'
        # Devuelve DDD*MM:SS#
        azimut = self.getPosicion(mensaje)
        azimut = azimut[0:3]+":"+azimut[4:-1]
        self.az = azimut
        return azimut

    # Obtiene la posicion en la que se encuentra el telescopio
    def getPosicion(self, mensaje):
        respuesta = self.serial.enviar(mensaje, respuesta = True)
        return respuesta


# ---------------------------------------------------------

    # Cada cierto tiempo obtiene la posicion del telescopio
    def seguimientoPosicion(self):
        self.aceptarThread = False
        t1 = 0
        tEspera = 0

        coordenadas0 = [0.0, 0.0]
        coordenadas1 = [0.0, 0.0]

        while (self.seguimiento == True or self.llegando == True):

            t2 = time.clock()

            if (t2-t1 >= tEspera):

                comparar = False
                llegandoModo = 'az-alt'

                if self.llegando == True:
                    comparar = True
                    #Evitamos bugs
                    llegandoModo = self.llegandoModo
                    if self.llegandoModo == 'az-alt':
                        coordenadas0[0] = self.toNumero(self.az)
                        coordenadas0[1] = self.toNumero(self.alt)

                    elif self.llegandoModo == 'ra-dec':
                        coordenadas0[0] = self.toNumero(self.ra)
                        coordenadas0[1] = self.toNumero(self.dec)

                self.ra = self.getRA()
                self.dec = self.getDec()
                self.az = self.getAz()
                self.alt = self.getAlt()

                gl.anadirAlLog('RA = ' + self.ra + ' DEC = '+self.dec+ ' AZ = '+self.az+' ALT = '+self.alt, 'INFO')

                if self.seguimiento == True:
                    self.cola.enviarMensaje(self.az, 'info')
                    gl.anadirAlLog('Mensaje publicado: AZ = '+self.az, 'INFO')

                if comparar == True:
                    if llegandoModo == 'az-alt':
                        coordenadas1[0] = self.toNumero(self.az)
                        coordenadas1[1] = self.toNumero(self.alt)

                    elif llegandoModo == 'ra-dec':
                        coordenadas1[0] = self.toNumero(self.ra)
                        coordenadas1[1] = self.toNumero(self.dec)

                    if self.estaMoviendose(coordenadas0, coordenadas1, 1.0) == False:
                        print('No se esta moviendo')
                        #########
                        self.llegando = False # Paramos
                        if self.haLlegado(coordenadas1, self.llegandoPosicion, 1.0) == True:
                            print('Ha llegado')
                            self.resultadoLlegando = "Sin incidencias"

                        else:
                            print('No ha llegado')
                            self.resultadoLlegando = "Error en el movimiento"
                            print(self.resultadoLlegando)

                # Historial de posiciones  ###################
                #self.posiciones.insert({'posicion': {'fecha': time.strftime("%d/%m/%y"), 'hora': time.strftime("%H:%M:%S"), 'coordenadas': {'ra': self.ra, 'dec': self.dec}}})
                t1 = time.clock()
                tEspera = self.tSeguimiento - (t1-t2) # intervalo de actualizacion - tiempo estimado que tardara
                #print 'Tiempo de espera: {}'.format(tEspera) #################

            time.sleep(0.1)

        self.aceptarThread = True
        print('Seguimiento finalizado')


    # Activa o desactiva el seguimiento
    def setSeguimiento(self,b, esperar=False):
        resultado = 'Nada ha cambiado'

        if (self.seguimiento == False and (b == True or esperar == True)):
            if self.aceptarThread == True:
                self.seguimiento = b
                th = Thread(target = self.seguimientoPosicion)
                th.start()
                resultado = 'Seguimiento iniciado'
            else:
                resultado = 'Antes de iniciar un nuevo seguimiento debe terminar el anterior'

        elif self.seguimiento == True and b == False:
            self.seguimiento = b
            resultado = 'Deteniendo seguimiento'
        return resultado
    # Podemos crear un thread aqui dentro

    # Cambiamos el tiempo entre obtener posiciones en el seguimiento
    def setTasaSeguimiento(self, tiempo):
        self.tSeguimiento = tiempo
        print('Tasa de seguimiento actualizada')

    # Ajustamos la velocidad de movimiento del telescopio
    def setSlewRate(self, n):
        print('Slew rate')

    def cambiarPermitirMovimiento(self, b):
        self.permitirMovimiento = b

    def estaMoviendose(self, coordenadas0, coordenadas1, margen):
        print('Margen: ')
        print(margen)
        # coordenadas 1 es la actual
        # coordenadas 0 es la anterior
        if (coordenadas0[0] >= coordenadas1[0] - margen) and (coordenadas1[0] + margen >= coordenadas0[0] ) and (coordenadas0[1] >= coordenadas1[1] - margen) and (coordenadas1[1] + margen >= coordenadas0[1]):
            return False

        return True

    def toNumero(self, coordenada):
        numero = 0;
        num = coordenada.split(':')
        i = 0
        signo = 0
        for x in num:
            if i == 0:
                numero = int(x)
                if numero < 0:
                    signo = -1
                else:
                    signo = 1
            else:
                numero = numero + signo*int(x)/60.0
            i = 1
        return numero

    def haLlegado(self, coordenadas1, coordenadas3, margen):
        # coordenadas 1 es la actual
        # coordenadas 3 es la objetivo
        print ('C10: ')
        print (coordenadas1[0])

        print ('C11: ')
        print (coordenadas1[1])

        print ('C30: ')
        print (coordenadas3[0])

        print ('C31: ')
        print (coordenadas3[1])

        if (coordenadas1[0] >= coordenadas3[0] - margen) and (coordenadas3[0] + margen >= coordenadas1[0]) and (coordenadas1[1] >= coordenadas3[1] - margen) and (coordenadas3[1] + margen >= coordenadas1[1] ):
            return True
        return False

    def setLlegandoModo(self, modo, posicion):
        self.llegandoModo = modo
        print(modo)
        self.llegandoPosicion[0] = self.toNumero(posicion[0])
        self.llegandoPosicion[1] = self.toNumero(posicion[1])

        print 'salir llegando'

    def esperarMovimiento(self,iden, setResultado):
        self.llegando = True
        self.resultadoLlegando = "Error. Tiempo excedido"
        self.setSeguimiento(self.seguimiento, esperar=True)
        while self.llegando == True:
            time.sleep(1)
        print (self.resultadoLlegando)
        setResultado(self.resultadoLlegando, iden)



# ------------------------------------------------------------------------


    # Mueve el telescopio en una direccion durante unos milisegundos
    def moverPorTiempo(self, direccion, tiempo = 500):
        print ('Mover por tiempo')
        if not self.permitirMovimiento:
            resultado = 'Movimiento no disponible'
            return resultado

        resultado = 'Sin incidencias'

        # ----- Para el telescopio del laboratorio ------
        # mensaje = ":Mg%s%s#" % (direccion, tiempo)

        # ----- Para el telescopio del observatorio ------
        mensajeIniciar = ':M{}#'.format(direccion)
        mensajeParar = ':Q{}#'.format(direccion)

        # Comienza el movimiento
        self.serial.enviar(mensajeIniciar) # No devuelve nada
        #print('Mensaje {} enviado').format(mensajeIniciar) #########
        # Paramos el movimiento tras un tiempo
        th = Timer(tiempo/1000.0, self.serial.enviar, [mensajeParar])
        th.start()
        # Esperamos a que envie este mensaje para continuar
        th.join()
        #print('Mensaje {} enviado').format(mensajeParar) ########
        return resultado

    # Mueve el telescopio a unas coordenadas dadas
    def moverPorCoordenadas(self, tipo, coordenadas):
        print ('Mover por coordenadas')

        if not self.permitirMovimiento:
            resultado = 'Movimiento no disponible'
            return resultado

        resultado = 'Sin incidencias'

        if tipo == 0: # az-alt

            g, m, s = coordenadas[1].split(':') #Grados, minutos, segundos
            mensaje = ":Sa{}*{}'{}#".format(g,m,s) # +00*00'00
            # Establecemos las coordenadas altitud del objetivo
            respuesta = self.serial.enviar(mensaje, respuesta = True)

            if respuesta != '1': # La montura devuelve un error
                return 'Error. No se ha podido establecer las coordenadas de altitud'

            # Coordenadas de altitud aceptadas. Continuamos con azimut	    
            g, m = coordenadas[0].split(':') # Grados, minutos
            mensaje = ":Sz{}*{}#".format(g,m) # 000*00
            respuesta = self.serial.enviar(mensaje, respuesta = True)

            if respuesta != '1': # La montura devuelve un error
                return 'Error. No se ha podido establecer las coordenadas de azimut'

            # Coordenadas de azimut aceptadas. Solicitamos el movimiento a la montura
            mensaje = ':MA#'
            respuesta = self.serial.enviar(mensaje, respuesta = True)
            if respuesta != '0': # La montura devuelve dos posibles errores
                return 'Error. Movimiento imposible. ' + respuesta[1:-1] # Filtramos el caracter que identifica el error


        elif tipo == 1: # RA-dec
            h, m = coordenadas[0].split(':') # Horas, minutos
            mensaje = ":Sr{}*{}#".format(h,m) # 00*00
            # Establecemos las coordenadas de ascension recta del objetivo
            respuesta = self.serial.enviar(mensaje, respuesta = True)

            if respuesta != '1': # La montura devuelve un error
                return 'Error. No se ha podido establecer las coordenadas de ascension recta'

            # Coordenadas de ascension recta aceptadas. Continuamos con declinacion
            g, m = coordenadas[1].split(':') # Grados, minutos
            mensaje = ":Sd{}*{}#".format(g,m) # +00*00
            print mensaje
            respuesta = self.serial.enviar(mensaje, respuesta = True)

            if respuesta != '1': # La montura devuelve un error
                return 'Error. No se ha podido establecer las coordenadas de declinacion'

            # Coordenadas de declinacion aceptadas. Solicitamos el movimiento		
            mensaje = ':MS#'
            respuesta = self.serial.enviar(mensaje, respuesta = True)	

            if respuesta != '0': # La montura devuelve dos posibles errores
                return 'Error. Movimiento imposible. ' + respuesta[1:-1]

        # Todo ha funcionado sin incidencias
        return resultado

    # Mueve el telescopio hacia un objeto dado
    def moverHastaObjeto(self, objeto):
        print('Mover hacia un objeto')

    # Movemos el telescopio hasta la posicion de home
    def moverAHome(self):
        print('Home')

    # Indicamos donde esta el home
    def setHome(self, home):
        print('Seleccionar el home')

    # Aparca el telescopio
    def park(self):
        mensaje = ':hP#'
        self.serial.enviar(mensaje)

    # Mover el telescopio en una direccion
    def moverNorte(self):
        mensaje = ':Mn#'
        self.serial.enviar(mensaje)            
    def moverSur(self):
        mensaje = ':Ms#'
        self.serial.enviar(mensaje)            
    def moverEste(self):
        mensaje = ':Me#'
        self.serial.enviar(mensaje)            
    def moverOeste(self):
        mensaje = ':Mw#'
        self.serial.enviar(mensaje)

    #Obtener la temperatura
    def temperatura(self):
	mensaje = ":fT#"
        respuesta = self.serial.enviar(mensaje, respuesta = True)
	print(respuesta)

    #Escribir cualquier comando que espere una respuesta y la imprime
    def comandoRespuesta(self,mensaje):
        respuesta = self.serial.enviar(mensaje, respuesta = True)
	print(respuesta)

    #Escribir un comando que no espera respuesta
    def comando(self,mensaje):
        self.serial.enviar(mensaje, respuesta = False)



    # Emplear?    
    def stop(self, noBloquear = False):
        self.permitirMovimiento = noBloquear
        mensaje = ':Q#'
        self.serial.enviar(mensaje)            
