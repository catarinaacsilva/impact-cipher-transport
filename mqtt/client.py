# coding: utf-8
​

__author__ = 'Catarina Silva'
__version__ = '0.1'
__email__ = 'c.alexandracorreia@av.it.pt'
__status__ = 'Development'


import os
import time
import json
import signal
import base64
import logging
import argparse
import paho.mqtt.client as mqtt


# configure logger output format
logging.basicConfig(level=logging.DEBUG,
format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',datefmt='%m-%d %H:%M:%S')
#format='%(message)s')

# get a logger to write
logger = logging.getLogger('dummy_sensor')

# used to stop the infinity loop
done = False

# rate that reads cpu load
rate = 1.0


def exit(signalNumber, frame):  
    global done
    done = True
    return
        

def on_connect(client, userdata, flags, rc):  
    logger.debug('Connected with result code {0}'.format(str(rc)))  
    client.subscribe('control/+/+/req/#', qos=0)  


def on_message(client, userdata, msg):
    t = time.time_ns()
    logger.info('Incoming topic: %s', msg.topic)
    #logger.info(msg.payload)
    incoming = json.loads(msg.payload)
    topic = incoming['topic']
    path = incoming['path']
    value = incoming['value']
    correlation_id = incoming['headers']['correlation-id']

    data = json.loads(base64.b64decode(value))
    logger.debug('On message {}'.format(data))
    global rate
    rate = data['rate']

    #logger.info('%d,%f', data['id'], t)
    
    #reply_topic = 'control///res/013command-and-controlreplies/200'
    req_id = msg.topic.split('/')[4]
    reply_topic = 'control///res/{}/200'.format(req_id)
    
    msg = {'topic': topic,
        'headers': {'content-type': 'application/json',
        'correlation-id': correlation_id},
        'path': path,
        'value': {'status': '200 OK'},
        'status': 200}
    #print(msg)
    logger.info('Topic %s', reply_topic)
    
    #msg={'status': 200}
    logger.info(msg)
    client.publish(reply_topic, json.dumps(msg), qos=0)
    return


def main(args):
    # register handler for interruption 
    # it stops the infinite loop gracefully
    signal.signal(signal.SIGINT, exit)
    
    global rate
    rate = args.r

    # MQTT client
    client = mqtt.Client('', protocol=mqtt.MQTTv311)
    client.on_connect = on_connect  
    client.on_message = on_message
    client.username_pw_set(args.u+'@'+args.t, password=args.p)
    client.enable_logger()
    logger.debug('Connect to %s', args.a)
    client.connect(args.a)
    client.loop_start()
    
    msg_id = 0

    while not done:
        cpu_load = os.getloadavg()
        msg = json.dumps({'id':msg_id, 'CPU Load': cpu_load[0]})
        client.publish('telemetry', msg, qos=0)
        t = time.time_ns()
        #logger.info('%d,%f',msg_id,t)
        logger.debug('MSG %s', msg)
        msg_id += 1
        time.sleep(rate)
    
    client.unsubscribe('control/+/+/req/#')
    client.loop_stop()
    client.disconnect()
    
    return 0


if __name__ == '__main__':
    # login: drtenant3 password: NkK9KAyMQsxZjwD3
    parser = argparse.ArgumentParser(description='dummy sensor')
    parser.add_argument('-a', type=str, help='Hono ip address', default='10.0.12.20')
    parser.add_argument('-t', type=str, help='tenant id', default='drtenant3')
    parser.add_argument('-d', type=str, help='device id', default='drdummy')
    parser.add_argument('-u', type=str, help='login', default='device_drdummy')
    parser.add_argument('-p', type=str, help='password', default='drdummysecret')
    parser.add_argument('-r', type=float, help='refresh rate', default='1.0')
    args = parser.parse_args()
    main(args)
