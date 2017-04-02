import pika
import config as c

credentials = pika.PlainCredentials('montura', 'meade')
connection = pika.BlockingConnection(pika.ConnectionParameters('192.168.1.119', 5672, '/', credentials))
channel = connection.channel()

channel.queue_declare(queue='telescopio', durable = True)

channel.exchange_declare(exchange='telescopio',
                         type='fanout')

channel.basic_publish(exchange='telescopio',
                      routing_key='Mensaje de la montura',
                      body=':D')
print(" [x] Sent 'Mensaje de la montura'")
connection.close()
