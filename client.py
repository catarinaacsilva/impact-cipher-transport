import time
import paho.mqtt.client as paho


broker = 

def on_message(client, userdata, message):
    time.sleep(1)
    print('received message =',str(message.payload.decode('utf-8')))

client= paho.Client('client0') 

client.on_message=on_message

print('connecting to broker ',broker)
client.connect(broker)
client.loop_start()

print('subscribing ')
client.subscribe(....)
time.sleep(2)

print('publishing ')
client.publish(.....)
time.sleep(4)

client.disconnect()
client.loop_stop()