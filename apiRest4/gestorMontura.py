from tinydb import TinyDB, Query
from montura import montura
import json
from threading import Thread, Timer

class gestorMontura:

    revisando = False
    revisar = True

# Base de datos
    db = TinyDB('database.json')
    tareas = db.table('tareas')
    posiciones = db.table('posiciones')
    q = Query()

    m = None
    def __init__(self):
        self.m = montura()

    # Devuelve el estado del telescopio en json
    def getStatus(self):
        [nombre, seguimiento, tSeguimiento, ra, dec, az, alt] = self.m.getStatus()
        return {'estado':{'nombre':nombre, 'seguimiento':seguimiento,
                                     'tasaSeguimiento':tSeguimiento,
                                     'ra':ra, 'dec':dec, 'az': az, 'alt':alt}}
    def getTareas(self):
        return self.tareas.all()

    def insertTarea(self, task):
        self.tareas.insert(task)

    def getTarea(self, iden):
        return self.tareas.search(self.q.id == iden)

    def revisarTareas(self):
        self.revisar = True
        if self.revisando == False:
            self.revisando = True
            th = Thread(target = self.procesarPeticiones)
            th.start()
            

    def procesarPeticiones(self):
        while self.revisar:
            self.revisar = False
            for task in self.tareas.search(self.q.done == False):
                self.procesarPeticion(task)
        self.revisando = False
        
    def setResultado(self, resultado, iden):
        print resultado
        print iden
        self.tareas.update({'resultado': resultado, 'done': True}, self.q.id == iden)

    def cancelarTimer(self):
        self.m.detenerMovimiento(noBloquear = True)
        self.m.llegando = False
        print 'Tiempo excedido...'
        
    # Identifica que debe hacer el telescopio
    def procesarPeticion(self, peticion):
        print('Procesar una peticion')
        # Anadimos la tarea a la base de datos
        iden = peticion['id']
        # Nos centramos en la orden a realizar
        peticion = peticion['orden']
        resultado = ''
        # Comprobamos las posibles ordenes
        if peticion['title'] == 'movement':
            if peticion['type'] == 'time': # mover un cierto tiempo
                if not 'dir' in peticion: # si no sabemos la direccion salimos
                    resultado = 'Error. Direccion del movimiento desconocida'
                elif not 'timer' in peticion: # valor por defecto
                    resultado = self.m.moverPorTiempo(peticion['dir'])
                else: # movemos en la direccion dada durante el tiempo indicado
                    resultado = self.m.moverPorTiempo(peticion['dir'], tiempo = int(peticion['timer']))
                
            elif peticion['type'] == 'coordinates': # mover a unas coordenadsa
                if not 'mode' in peticion: # si no sabemos el modo salimos
                    resultado = 'Error. No se ha indicado el tipo de coordenadas'
                if not 'coordenadas' in peticion:
                    resultado = 'Error. No se han indicado las coordenadas'
                elif peticion['mode'] == 'az-alt': # azimut-altitud
                    az = peticion['coordenadas']['az']
                    alt = peticion['coordenadas']['alt']
                    coordenadas = [az, alt]
                    resultado = self.m.moverPorCoordenadas(0, coordenadas)
                    self.m.setLlegandoModo("az-alt", coordenadas)
                elif peticion['mode'] == 'RA-dec': # ascension recta - declinacion
                    ra = peticion['coordenadas']['RA']
                    dec = peticion['coordenadas']['dec']
                    coordenadas = [ra, dec]
                    resultado = self.m.moverPorCoordenadas(1, coordenadas)
                    self.m.setLlegandoModo('ra-dec', coordenadas)
                else: # ninguno
                    resultado = 'Error. Tipo de coordenadas desconocido. Soportadas: az-alt / RA-dec'

                if resultado == 'Sin incidencias':
                    resultado = None
                    t1 = Thread(target = self.m.esperarMovimiento, args = (iden, self.setResultado))
                    t1.start()
                    t = Timer(60, self.cancelarTimer, args=())
                    t.start()
                    t1.join() # ha terminado
                    t.cancel() # ya no hace falta el timer
        
        elif peticion['title'] == 'seguimiento':
            if not 'type' in peticion:
                resultado = 'Error. No se indica que se debe hacer'
            elif peticion['type'] == 'estado':
                if not 'activo' in peticion: # encendemos o apagamos?
                    resultado = 'Error. No se indica el estado deseado del seguimiento'
                else:
                    resultado = self.m.setSeguimiento(peticion['activo'])
            elif peticion['type'] == 'intervalo':
                if not 'intervalo' in peticion:
                    resultado = 'Error. No se indica el intervalo'
                elif int(peticion['intervalo']) < self.m.tSeguimientoMin:
                    resultado = 'Error. El intervalo minimo es {}'.format(self.m.tSeguimientoMin)
                elif int(peticion['intervalo']) > self.m.tSeguimientoMax:
                    resultado = 'Error. El intervalo maximo es {}'.format(self.m.tSeguimientoMax)
                else:
                    self.m.setTasaSeguimiento(int(peticion['intervalo']))          
                   
        # Actualizamos la tarea y finalizamos su procesamiento
        if resultado != None:
            self.setResultado(resultado, iden)
        #self.tareas.update({'resultado': resultado, 'done': True}, self.q.id == iden)
	print('Final del procesado')
	return resultado
