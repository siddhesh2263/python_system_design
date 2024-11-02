import pika, sys, os, time
from send import email

def main():

    # rabbitmq connection
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host="rabbitmq")
    )

    def callback(ch, method, properties, body):
        err = email.notification(body)
        if err:
            # if error, want to send a negative acknowledgement. so the message won't be removed
            # from the queue. the delivery_tag uniquely identifies the delivery on the channel.
            ch.basic_nack(delivery_tag=method.delivery_tag)
        else:
            ch.basic_ack(delivery_tag=method.delivery_tag)
    
    channel = connection.channel()

    channel.basic_consume(
        queue=os.environ.get("MP3_QUEUE"),
        on_message_callback=callback
    )

    print("Waiting for messages. To exit press Ctrl+C")

    # the consumer will start listening
    channel.start_consuming()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)