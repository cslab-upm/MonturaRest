#!/bin/python
# coding: utf-8

import pika
class RabbitMQ_sender:
    '''Clase de un dispositivo que enviará mensajes a un exchange de RabbitMQ con su nombre'''
    def __init__(self,my_name,server_ip="localhost"):
        '''Inicialización. Parámetros:
    my_name: string    Nombre del dispositivo. Se corresponde con el nombre del exchange al que va a publicar
    server_ip: string  Dirección IP del servidor de RabbitMQ (Opcional, 'localhost' por omisión).
    '''
	self.credentials = pika.PlainCredentials("","")
        connection = pika.BlockingConnection(
                pika.ConnectionParameters(server_ip,5672,'/',self.credentials))
		#pika.ConnectionParameters(host=server_ip))
        channel = connection.channel()
        self.my_name=my_name
        self.server_ip = server_ip
        # Declarar el exchage al que se va a publicar
        channel.exchange_declare(exchange=my_name,
                    exchange_type="direct")
        connection.close()
    def send_message(self,severity,message):
        '''Envía un mensaje. Parámetros:
    severity: 'info' | 'critical'  Importancia del mensaje
    message: String                Cuerpo del mensaje
'''
	connection = pika.BlockingConnection(
                pika.ConnectionParameters(self.server_ip,5672,'/',self.credentials))

        channel = connection.channel()

        channel.basic_publish(exchange=self.my_name,
                routing_key=severity,
                body=message)
        connection.close()
   
        

class RabbitMQ_receiver:
    'Clase de un dispositivo que recibirá mensajes de RabbitMQ'
    def __init__(self,subscription,callback,ip_server='localhost'):
        '''Inicialización. Parámetros:
    subscription: Subscription      Colas y prioridaded de las que se quiere leer

    
    ip_server:  string      Dirección IP del servidor de RabbitMQ
    
    callback:   Funcion(severity,message) que se ejecutará cada vez que llegue
                un mensaje. El parametro severity contendrá la importancia y
                el parametro message, el cuerpo del mensaje.
'''
        credentials = pika.PlainCredentials("","")
        self.connection = pika.BlockingConnection(
                pika.ConnectionParameters(ip_server,5672,'/',credentials))

        self.channel = self.connection.channel()
        self.callback = callback

        if subscription:
            self.name=self.channel.queue_declare(exclusive=True).method.queue
            for s in subscription.subscriptions:

                # Declarar el exchange del que se quiere recibir, por si se
                # ejecuta antes que el emisor correspondiente
                self.channel.exchange_declare(exchange=s['queue'],
                        exchange_type="direct")

                # Avisar de que se quiere escuchar del exchange correspondiente
                self.channel.queue_bind(exchange=s['queue'],
                        queue=self.name,
                        routing_key=s['severity'])
    def start_consuming(self):
        def callback(ch,method,properties,body):
            return self.callback(method.routing_key,body.decode())

        self.channel.basic_consume(callback,
                queue=self.name,
                no_ack=True)
        print("[x] Iniciado el consumo en {}".format(self.name))
        self.channel.start_consuming()
    def __del__(self):
        self.connection.close()

class Subscription:
    def __init__(self,*subs):
        self.subscriptions = [{'queue':s.split(':')[0],
            'severity':s.split(':')[1]} for 
            s in subs if len(s.split(':')) == 2]
    def add_subscription(self,*subs):
        self.subscriptions.extend( [{'queue':s.split(':')[0],
            'severity':s.split(':')[1]} for 
            s in subs if len(s.split(':')) == 2])
        
