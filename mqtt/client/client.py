# coding: utf-8

__author__ = 'Catarina Silva'
__version__ = '0.1'
__email__ = 'c.alexandracorreia@av.it.pt'
__status__ = 'Development'


import time
import json
import signal
import logging
import argparse
import requests
import paho.mqtt.client as mqtt

from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey, X25519PublicKey
from cryptography.hazmat.primitives import serialization
#from cryptography.hazmat.primitives.asymmetric import x25519
#from cryptography.hazmat.primitives.kdf.hkdf import HKDF

# configure logger output format
logging.basicConfig(level=logging.DEBUG,format='%(message)s')
logging.getLogger("requests").setLevel(logging.WARNING)

# get a logger to write
logger = logging.getLogger('Client')

# used to stop the infinity loop
done = False


# define the subscription topic
topic = 'sensor/bme280'

def exit(signalNumber, frame):  
    global done
    done = True
    return


def on_message(client, userdata, message):
    data = json.loads(msg.payload)
    logger.info(data)
    

def on_connect(client, userdata, flags, rc):  
    logging.debug('Connected with result code {0}'.format(str(rc)))  
    client.subscribe(topic, qos=0)  


def main(args):
    # setup
    logger.info('Setup')
    private_key = X25519PrivateKey.generate()
    public_key = private_key.public_key()
    public_bytes = public_key.public_bytes(encoding=serialization.Encoding.Raw, format=serialization.PublicFormat.Raw)
    logger.info('Public Key = %s', public_bytes.hex())

    # share public key
    reply = requests.post('{}/putkey'.format(args.ke), json={'id':'client', 'pubkey': public_bytes.hex()})
    code = reply.status_code
    while(int(code/100) != 2):
        time.sleep(3.0)
        reply = requests.post('{}/putkey'.format(args.ke), json={'id':'client', 'pubkey': public_bytes.hex()})
        code = reply.status_code
    logger.info('Public Key registered')

    # request public key
    reply = requests.get('{}/getkey/sensor'.format(args.ke))
    code = reply.status_code
    while(int(code/100) != 2):
        time.sleep(3.0)
        reply = requests.get('{}/getkey/sensor'.format(args.ke))
        code = reply.status_code
    sensor_public_key_bytes = bytes.fromhex(reply.json()['key'])
    sensor_public_key = X25519PublicKey.from_public_bytes(sensor_public_key_bytes)

    shared_key = private_key.exchange(sensor_public_key)

    logger.info(shared_key.hex())

    # create a signal to terminate the client
    signal.signal(signal.SIGINT, exit)

    #create new instance
    logging.debug('create new instance')
    client = mqtt.Client()

    client.on_connect = on_connect

    #attach function to callback
    logging.debug('attach function to callback')
    client.on_message=on_message

    #connect to broker
    logging.debug('connect to broker')
    client.connect('localhost')

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


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='IoT MQTT Client')
    parser.add_argument('--ke', type=str, help='KeyExchange URL', default='http://localhost:5000')
    args = parser.parse_args()
    main(args)
