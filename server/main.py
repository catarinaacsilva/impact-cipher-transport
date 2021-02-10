# coding: utf-8

__author__ = 'Catarina Silva'
__version__ = '0.1'
__email__ = 'c.alexandracorreia@av.it.pt'
__status__ = 'Development'

import logging

from flask import Flask, request, jsonify

# Logger configuration
logging.basicConfig(level=logging.DEBUG, format='%(message)s\n')
werkzeug = logging.getLogger('werkzeug')
werkzeug.setLevel(logging.WARNING)
logger = logging.getLogger('ES')

# Database for the public keys
pubkeys = {}

# Database for data
data = {}

# Create a Flask HTTP server
app = Flask(__name__)


@app.route('/')
def hello():
    return 'Hello World!'

@app.route('/getkey/<idD>', methods=['GET'])
def get_key(idD):
    if idD in pubkeys:
        keys = pubkeys[idD]
        if len(keys) > 0:
            d = {'key': keys.pop(0)}
            logger.debug('getkey (%s, %s)', idD, d)
            return jsonify(d)
        else :
            return ('', 400)
    else:
        return ('', 400)

@app.route('/putdata/<idD>', methods=['POST'])
def put_data(idD):
    if request.is_json:
        content = request.get_json()
        logger.debug('putdata (%s, %s)', idD, content)
        data[idD] = content
        return ('', 204)
    else:
        return ('', 400)

@app.route('/getdata/<idD>', methods=['GET'])
def get_data(idD):
    if idD in data:
        d = data.pop(idD)
        logger.debug('getdata (%s, %s)', idD, d)
        return jsonify(d)
    else:
        return ('', 400)

@app.route('/putkey/<idD>', methods=['POST'])
def put_key(idD):
    if request.is_json:
        content = request.get_json()
        logger.debug('putkey (%s, %s)', idD, content['pubkey'])
        if idD in pubkeys:
            pubkeys[idD].append(content['pubkey'])
        else:
            pubkeys[idD] = [content['pubkey']]
        return ('', 204)
    else:
        return ('', 400)


if __name__ == '__main__':
    app.run(host='0.0.0.0')
