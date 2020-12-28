import paho.mqtt.client as mqtt
import time
import logging
import signal
import json

done = False

def exit(signalNumber, frame):  
    global done
    done = True
    return

def on_message(client, userdata, message):
    incoming = json.loads(msg.payload)
    topic = incoming['topic']
    value = incoming['value']

    msg = {'topic': topic,
        'headers': {'content-type': 'application/json',
        'value': {'status': '200 OK'},
        'status': 200}

def on_connect(client, userdata, flags, rc):  
    logging.debug('Connected with result code {0}'.format(str(rc)))  
    client.subscribe('house/light', qos=0)  


def main():
    signal.signal(signal.SIGINT, exit)

    client_name = 'C1'
    #broker ip address 
    host_name = 'localhost'

    #create new instance
    logging.debug('create new instance')
    client =mqtt.Client(client_name)

    client.on_connect = on_connect

    #attach function to callback
    logging.debug('attach function to callback')
    client.on_message=on_message

    #connect to broker
    logging.debug('connect to broker')
    client.connect(host_name)

    #start the loop
    logging.debug('start the loop')
    client.loop_start()

    while not done:
        # wait
        logging.debug('wait')
        time.sleep(4)
        #stop the loop
        logging.debug('stop the loop')
    
    client.unsubscribe('house/light')
    client.loop_stop() 
    client.disconnect()

    return 0

main()
