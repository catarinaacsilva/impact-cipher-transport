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
import statistics


# MQTT library
import paho.mqtt.client as mqtt


# convert datetime to string and vice versa
from datetime import datetime


# Cryptography libraries
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey, X25519PublicKey
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import serialization


# Libraries to use enumerate
from enum import Enum


# Enum that defines the DF key exchange algorithm
class DH(Enum) :
    curve25519 = 'curve25519'
    p521 = 'p521'

    def __str__(self):
        return self.value


# Enum that defines the Cipher algorithm
class CA(Enum):
    aes = 'aes'
    chacha = 'chacha'

    def __str__(self):
        return self.value


# Enum that defines the Cipher algorithm key size
class KS(Enum):
    s128 = '128'
    s192 = '192'
    s256 = '256'

    def __str__(self):
        return self.value


# configure logger output format
logging.basicConfig(level=logging.DEBUG,format='%(message)s')
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)


# get a logger to write
logger = logging.getLogger('Client')


# used to stop the infinity loop
done = False


# list that store the delays
sensor_cypher = []
transport = []
client_decrypt = []


# Session key
session_key = None


def exit(signalNumber, frame):  
    global done
    done = True


def init_session(args, local='client', peer='sensor'):
    logger.info('Init Session')

    start = time.perf_counter()
    if args.d is DH.curve25519:
        private_key = X25519PrivateKey.generate()
        public_key = private_key.public_key()
        public_bytes = public_key.public_bytes(encoding=serialization.Encoding.Raw, format=serialization.PublicFormat.Raw)    
    elif args.d is DH.p521:
        private_key = ec.generate_private_key(ec.SECP521R1())
        public_key = private_key.public_key()
        public_bytes = public_key.public_bytes(encoding=serialization.Encoding.X962, format=serialization.PublicFormat.UncompressedPoint)
    duration1 = time.perf_counter() - start
    logger.info('Public Key = %s', public_bytes.hex())

    # share public key
    reply = requests.post('{}/putkey/{}'.format(args.u, local), json={'pubkey': public_bytes.hex()})
    code = reply.status_code
    while int(code/100) != 2:
        time.sleep(1.0)
        reply = requests.post('{}/putkey/{}'.format(args.u, local), json={'pubkey': public_bytes.hex()})
        code = reply.status_code
    logger.info('Public Key registered')

    # request public key
    reply = requests.get('{}/getkey/{}'.format(args.u, peer))
    code = reply.status_code
    while int(code/100) != 2:
        time.sleep(1.0)
        reply = requests.get('{}/getkey/{}'.format(args.u, peer))
        code = reply.status_code
    sensor_public_key_bytes = bytes.fromhex(reply.json()['key'])
    
    start = time.perf_counter()
    if args.d is DH.curve25519:
        sensor_public_key = X25519PublicKey.from_public_bytes(sensor_public_key_bytes)
        shared_key = private_key.exchange(sensor_public_key)
    elif args.d is DH.p521:
        sensor_public_key = ec.EllipticCurvePublicKey.from_encoded_point(ec.SECP521R1(), sensor_public_key_bytes)
        shared_key = private_key.exchange(ec.ECDH(), sensor_public_key)
    duration2 = time.perf_counter() - start
    logger.info('Shared key: %s', shared_key.hex())

    if args.c is CA.chacha or args.k is KS.s256:
        session_key = shared_key[:32]
    elif args.k is KS.s192:
        session_key = shared_key[:24]
    elif args.k is KS.s128:
        session_key = shared_key[:16]

    logger.info('Session key: %s', session_key.hex())
    delay = (duration1 + duration2) * 1E6
    return session_key, int(round(delay))


def get_data(args):
    reply = requests.get('{}/getdata/client'.format(args.u))
    code = reply.status_code
    while int(code/100) != 2:
        time.sleep(1.0)
        reply = requests.get('{}/getdata/client'.format(args.u))
        code = reply.status_code
    return reply.json()


def decrypt(key, iv, ciphertext):
    decryptor = None
    if args.c is CA.aes:
        decryptor = Cipher(algorithms.AES(key), modes.CTR(iv)).decryptor()
    elif args.c is CA.chacha:
        decryptor = Cipher(algorithms.ChaCha20(key, iv), mode=None).decryptor()
    return decryptor.update(ciphertext) + decryptor.finalize()


def on_connect(client, userdata, flags, rc):  
    logger.debug('Connected with result code {0}'.format(str(rc)))  
    client.subscribe('sensor/bme280') 


def on_message(client, userdata, msg):
    logger.info('Incoming topic: %s', msg.topic)
    logger.debug(msg.payload)
    data = json.loads(msg.payload)

    # Transport duration
    now = datetime.now()
    then = datetime.strptime(data['time'], '%Y-%m-%d %H:%M:%S.%f')
    result = now - then
    transport_duration = result.total_seconds() * 1e6 + result.microseconds
    transport.append(int(round(transport_duration)))

    # Process the remaining information
    logger.info(data)
    #sensor_key.append(data['key_delay'])
    sensor_cypher.append(data['cipher_delay'])
    iv = bytes.fromhex(data['iv'])
    cipher = bytes.fromhex(data['cipher'])
    start = time.perf_counter()
    plain = decrypt(session_key, iv, cipher).decode('ascii')
    duration = (time.perf_counter() - start)*1E6
    client_decrypt.append(int(round(duration)))
    logger.info(plain)


def main(args):
    # create a signal to terminate the client
    signal.signal(signal.SIGINT, exit)

    # setup the session key
    global session_key
    session_key, delay = init_session(args)
    logger.info("Key delay %s", delay)

    client = mqtt.Client('client')
    client.on_connect = on_connect  
    client.on_message = on_message
    client.connect(args.b, args.p)
    
    while not done:
        client.loop()
    
    # Print results
    logger.info('Sensor cypher delay : %s±%s (μs)', statistics.mean(sensor_cypher), statistics.stdev(sensor_cypher))
    logger.info('Tranport delay      : %s±%s (μs)', statistics.mean(transport), statistics.stdev(transport))
    logger.info('Client decrypt delay: %s±%s (μs)', statistics.mean(client_decrypt), statistics.stdev(client_decrypt))
    return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='IoT MQTT Client')
    parser.add_argument('-u', type=str, help='KeyExchange URL', default='http://localhost:5000')
    parser.add_argument('-b', type=str, help='MQTT broker (address)', default='localhost')
    parser.add_argument('-p', type=int, help='MQTT broker (port)', default=1883)
    parser.add_argument('-d', type=DH, help='Diffie–Hellman key exchange', choices=list(DH), default='curve25519')
    parser.add_argument('-k', type=KS, help='Symmetric key size', choices=list(KS), default='128')
    parser.add_argument('-c', type=CA, help='Cipher algorithm', choices=list(CA),  default='aes')
    args = parser.parse_args()
    main(args)
