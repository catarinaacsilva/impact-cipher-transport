# coding: utf-8

__author__ = 'Catarina Silva'
__version__ = '0.1'
__email__ = 'c.alexandracorreia@av.it.pt'
__status__ = 'Development'


import os
import time
import json
import signal
import logging
import argparse
import requests


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


# BME280 and BMP280
import board
import adafruit_bmp280
from adafruit_bme280 import basic as adafruit_bme280


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


# Enum that defines the Cipher algorithm
class KS(Enum):
    s128 = '128'
    s192 = '192'
    s256 = '256'

    def __str__(self):
        return self.value


# Enum for the sensor type
class ST(Enum):
    bmp280='bmp280'
    bme280='bme280'

    def __str__(self):
        return self.value


# configure logger output format
logging.basicConfig(level=logging.DEBUG,format='%(message)s')
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)


# get a logger to write
logger = logging.getLogger('Sensor')


# used to stop the infinity loop
done = False


def exit(signalNumber, frame):  
    global done
    done = True


def init_session(args, local='sensor', peer='client'):
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
        time.sleep(3.0)
        reply = requests.post('{}/putkey/{}'.format(args.u, local), json={'pubkey': public_bytes.hex()})
        code = reply.status_code
    logger.info('Public Key registered')

    # request public key
    reply = requests.get('{}/getkey/{}'.format(args.u, peer))
    code = reply.status_code
    while int(code/100) != 2:
        time.sleep(3.0)
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


def encrypt(key, iv, plain, args):
    p = str.encode(plain)
    encryptor = None
    if args.c is CA.aes:
        encryptor = Cipher(algorithms.AES(key), modes.CTR(iv)).encryptor()
    elif args.c is CA.chacha:
        encryptor = Cipher(algorithms.ChaCha20(key, iv), mode=None).encryptor()
    return encryptor.update(p) + encryptor.finalize()


def main(args):
    # create a signal to terminate the client
    signal.signal(signal.SIGINT, exit)

    # setup the session key
    session_key, key_delay = init_session(args)

    client = mqtt.Client('sensor')
    client.connect(args.b, args.p)

    if args.s is ST.bmp280:
        i2c = board.I2C()  # uses board.SCL and board.SDA
        sensor = adafruit_bmp280.Adafruit_BMP280_I2C(i2c)
        sensor.sea_level_pressure = 1013.25
    else:
        i2c = board.I2C()  # uses board.SCL and board.SDA
        sensor = adafruit_bme280.Adafruit_BME280_I2C(i2c)
        sensor.sea_level_pressure = 1013.25

    while not done:
        # read values from sensor
        t = sensor.temperature
        if args.s is ST.bmp280:
            h = 0.0
        else:
            h = sensor.humidity    
        p = sensor.pressure

        data = json.dumps({'temperature': t, 'humidity': h, 'pressure': p})
        
        iv = os.urandom(16)
        
        start = time.perf_counter()
        ciphertext = encrypt(session_key, iv, data, args)
        cipher_delay = (time.perf_counter() - start)*1E6
        

        now = datetime.now()
        reply = {'cipher': ciphertext.hex(), 'iv': iv.hex(), 'key_delay': key_delay,
        'cipher_delay':cipher_delay, 'time':now.strftime('%Y-%m-%d %H:%M:%S.%f')}

        logger.info(reply)
        client.publish('sensor/bme280', json.dumps(reply))
        client.loop()
        time.sleep(1.0)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='RPi sensor')
    parser.add_argument('-u', type=str, help='KeyExchange URL', default='http://localhost:5000')
    parser.add_argument('-b', type=str, help='MQTT broker (address)', default='localhost')
    parser.add_argument('-p', type=int, help='MQTT broker (port)', default=1883)
    parser.add_argument('-d', type=DH, help='Diffie–Hellman key exchange', choices=list(DH), default='curve25519')
    parser.add_argument('-k', type=KS, help='Symmetric key size', choices=list(KS), default='128')
    parser.add_argument('-c', type=CA, help='Cipher algorithm', choices=list(CA),  default='aes')
    parser.add_argument('-s', type=ST, help='Sensor type',  choices=list(ST), default='bmp280')
    args = parser.parse_args()
    main(args)
