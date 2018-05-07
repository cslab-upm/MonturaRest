from montura import montura
import json, time
import rabbitmq_device as rmq
from threading import Thread, Timer


#Espera un json del tipo {"comando":"moverNorte", "parametros":[]}
def callbackPasarela(severity,message):
	message = json.loads(message)
        #Comprueba si hay parametros o no
	if not 'parametros' in message:
		message["parametros"]=[]
	#print(message["comando"])
        #Llama a la operacion con los parametros
	#TODO Poner un try catch para evitar que rompa el programa una llamada mal formada.
	operaciones[str(message["comando"])](*message["parametros"])
	

#Funcion comunica la posicion Azimut
def comunicarAzimut(montura, sender):
	while True:
    		grados = montura.getAz()[0:3]
		#Solo envia mensajes si recibe el azimut y la altura bien
		if grados.isdigit():
			#print(grados)
			#mensaje = json.dumps({'azimuth':int(grados)})
    			altura = montura.getAzlt()[0:3]
			if altura.isdigit():
				mensaje = json.dumps({'azimuth':int(grados),'altura':int(altura)})
    				sender.send_message('info',mensaje)
    		print(grados)
    		time.sleep(10)

#Montura
montura = montura()

#Operaciones permitidas a los mensajes recibidos de rabbitMQ
#Se pueden anyadir todas las que se quieran
operaciones = {
	"moverNorte":montura.moverNorte(),
	"parar":montura.stop,
	"moverEste":montura.moverEste(),
	"moverOeste":montura.moverOeste(),
	"moverSur":montura.moverSur()
}

def main():

	sender = rmq.RabbitMQ_sender('montura', "192.168.1.5")
	emisor_posicion = Thread(target = comunicarAzimut, args=(montura, sender))
	emisor_posicion.start()

	subscription = rmq.Subscription('pasarela:info','pasarela:critical')
	receiver = rmq.RabbitMQ_receiver(subscription, callbackPasarela,"192.168.1.5")
	receiver.start_consuming()

if __name__ == '__main__':
    main() 
