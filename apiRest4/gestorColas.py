import pika
import config as c
from montura import montura

class gestorColas:

    montura = None
    credentials = pika.PlainCredentials('venus', 'informaticaciclope')
    parameters = pika.ConnectionParameters('venus.datsi.fi.upm.es',5672, '/',credentials)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    
    def setMontura(self, montura):
        self.montura = montura

    def iniciarCola(self):
        
        
        self.channel.queue_declare(queue=c.me, durable = True)
        self.channel.exchange_declare(exchange=c.me, type='fanout')
        for x in c.lista:
                self.channel.queue_declare(queue=x, durable=True)

        for x,y in zip(c.lista,c.severity):
                self.channel.exchange_declare(exchange=x,
                                        type='fanout')
                self.channel.queue_bind(exchange=x,
                                   queue=c.me,
                                   routing_key=y)

        def callback(ch, method, properties, body):
            print(" [x] Received %r" % body)
            self.procesarMensaje(body)

        self.channel.basic_consume(callback, queue=c.me, no_ack=True)

        print(' [*] Waiting for messages. To exit press CTRL+C')
        self.channel.start_consuming()

    def procesarMensaje(self, mensaje):
        if (mensaje == 'parar'):
            print 'parando...'
            self.montura.cambiarPermitirMovimiento(False)
        elif (mensaje == 'continuar'):
            print 'reanudando...'
            self.montura.cambiarPermitirMovimiento(True)
            
    def enviarMensaje(self, mensaje, severity):
        self.channel.basic_publish(exchange=c.me,
                      routing_key=severity,
                      body=mensaje)
        
