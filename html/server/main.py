# coding: utf-8

__author__ = 'Catarina Silva'
__version__ = '0.1'
__email__ = 'c.alexandracorreia@av.it.pt'
__status__ = 'Development'

import logging

from flask import Flask, request, jsonify

# Logger configuration
logging.basicConfig(level=logging.DEBUG, format='%(message)s')
werkzeug = logging.getLogger('werkzeug')
werkzeug.setLevel(logging.WARNING)
logger = logging.getLogger('ES')

# Database for the public keys
pubkeys = {}

# Database for data
data = {}

# Create a Flask HTTP server
app = Flask(__name__)

# explicar como a api funciona
@app.route('/')
def hello():
    return 'Hello World!'

@app.route('/getkey/<idD>', methods=['GET'])
def get_key(idD):
    if idD in pubkeys:
        d = {'key': pubkeys.pop(idD)}
        return jsonify(d)
    else:
        return ('', 400)

@app.route('/putdata/<idD>', methods=['POST'])
def put_data(idD):
    if request.is_json:
        content = request.get_json()
        logger.debug(content)
        data[idD] = content
        return ('', 204)
    else:
        return ('', 400)

@app.route('/getdata/<idD>', methods=['GET'])
def get_data(idD):
    if idD in data:
        d = data.pop(idD)
        return jsonify(d)
    else:
        return ('', 400)

@app.route('/putkey', methods=['POST'])
def put_key():
    if request.is_json:
        content = request.get_json()
        idD = content['id']
        pubkey = content['pubkey']
        logger.debug('putkey (%s, %s)', idD, pubkey)
        pubkeys[idD]=pubkey
        return ('', 204)
    else:
        return ('', 400)


if __name__ == '__main__':
    app.run(host='0.0.0.0')
