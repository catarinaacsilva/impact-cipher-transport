# coding: utf-8
​

__author__ = 'Catarina Silva'
__version__ = '0.1'
__email__ = 'c.alexandracorreia@av.it.pt'
__status__ = 'Development'

import logging 

from flask import Flask, request, jsonify

app = Flask(__name__)

pubkeys = {}

# explicar como a api funciona
@app.route('/')
def hello():
    return 'Hello World!'

@app.route('/getkey/<idD>', methods=['GET'])
def getKey(idD):
    #idD = request.args.get('id')
    if idD in pubkeys:
        d = {'key': pubkeys[idD]}
        return jsonify(d)
    else:
        logging.error('id in not in database')
        return jsonify({})


@app.route('/putkey', methods=['POST'])
def putKey():
    if request.is_json:
        content = request.get_json()
        idD = content['id']
        pubkey = content['pubkey']
        pubkeys[idD]=pubkey
        return ('', 204)
    else:
        logging.error('This is an error message')



if __name__ == '__main__':
    app.run()