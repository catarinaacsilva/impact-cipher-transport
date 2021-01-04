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

from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey, X25519PublicKey
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import serialization

# configure logger output format
logging.basicConfig(level=logging.DEBUG,format='%(message)s')
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

# get a logger to write
logger = logging.getLogger('Client')

# used to stop the infinity loop
done = False

def exit(signalNumber, frame):  
    global done
    done = True
    return

def init_session(args):
    # setup
    logger.info('Init Session')
    start = time.perf_counter()
    private_key = X25519PrivateKey.generate()
    public_key = private_key.public_key()
    public_bytes = public_key.public_bytes(encoding=serialization.Encoding.Raw, format=serialization.PublicFormat.Raw)
    duration1 = time.perf_counter() - start
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
    start = time.perf_counter()
    sensor_public_key = X25519PublicKey.from_public_bytes(sensor_public_key_bytes)
    shared_key = private_key.exchange(sensor_public_key)
    duration2 = time.perf_counter() - start
    logger.info('Shared key: %s', shared_key.hex())
    session_key = shared_key[:16]
    logger.info('Session key: %s', session_key.hex())

    delay = (duration1 + duration2) * 1E6

    return session_key, int(round(delay))


def get_data(args):
    reply = requests.get('{}/getdata/client'.format(args.ke))
    code = reply.status_code
    while(int(code/100) != 2):
        time.sleep(1.0)
        reply = requests.get('{}/getdata/client'.format(args.ke))
        code = reply.status_code
    return reply.json()


def decrypt(key, iv, ciphertext):
    decryptor = Cipher(algorithms.AES(key), modes.CTR(iv)).decryptor()
    return decryptor.update(ciphertext) + decryptor.finalize()


def main(args):
    # create a signal to terminate the client
    signal.signal(signal.SIGINT, exit)

    sensor_key = []
    sensor_cypher = []
    transport = []
    client_key = []
    client_decrypt = []
    msg_length = []

    while not done:
        session_key, delay = init_session(args)
        logger.info("Key delay %s", delay)
        client_key.append(delay)
        data = get_data(args)
        now = int(time.time())
        transport.append((now - data['time']))
        logger.info(data)
        sensor_key.append(data['key_delay'])
        sensor_cypher.append(data['cypher_delay'])
        iv = bytes.fromhex(data['iv'])
        cipher = bytes.fromhex(data['cypher'])
        start = time.perf_counter()
        plain = decrypt(session_key, iv, cipher).decode('ascii')
        duration = (time.perf_counter() - start)*1E6
        logger.info('Message %s Real %s', len(data['cypher'] + data['iv']), len(plain))
        msg_length.append((len(data['cypher'] + data['iv'])/len(plain))-1.0)
        client_decrypt.append(int(round(duration)))
        logger.info(plain)
    
    # Print results
    logger.info('Sensor key delay    : %s±%s (μs)', statistics.mean(sensor_key), statistics.stdev(sensor_key))
    logger.info('Sensor cypher delay : %s±%s (μs)', statistics.mean(sensor_cypher), statistics.stdev(sensor_cypher))
    logger.info('Tranport delay      : %s±%s (s)', statistics.mean(transport), statistics.stdev(transport))
    logger.info('Client key delay    : %s±%s (μs)', statistics.mean(client_key), statistics.stdev(client_key))
    logger.info('Client decrypt delay: %s±%s (μs)', statistics.mean(client_decrypt), statistics.stdev(client_decrypt))
    logger.info('Msg Ratio           : %s±%s (μs)', statistics.mean(msg_length), statistics.stdev(msg_length))
    return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='IoT MQTT Client')
    parser.add_argument('--ke', type=str, help='KeyExchange URL', default='http://localhost:5000')
    args = parser.parse_args()
    main(args)
