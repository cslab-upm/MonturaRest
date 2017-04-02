import pika
import config as c

credentials = pika.PlainCredentials('montura', 'meade')
parameters = pika.ConnectionParameters(c.urlServer,5672, '/',credentials)
connection = pika.BlockingConnection(parameters)
channel = connection.channel()
channel.queue_declare(queue=c.me, durable = True)
channel.exchange_declare(exchange='cupula',
                         type='fanout')
channel.queue_bind(exchange='cupula',
                       queue=c.me,
                       routing_key='aaa')

def callback(ch, method, properties, body):
    print(" [x] Received %r" % body)
    # cosas a hacer
    # --------

channel.basic_consume(callback, queue=c.me, no_ack=True)

print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()
