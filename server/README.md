# HTTP Server

This is the code for the simple HTTP Server that offer two functionalities:

1. Repository for Public Key exchange
2. Repository for data exchange

## API

### Put Key

**URL** : `/putkey/<idD>`
**Method** : `POST`
**Data constraints**:
```json
{
  "pubkey": "[valid ECDH public key]"
}
```
#### Success Response
**Code** : `204 NO CONTENT`

#### Error Response
**Code** : `400 BAD REQUEST`


### Get Key

**URL** : `/getkey/<idD>`
**Method** : `GET`

#### Success Response
**Code** : `200 OK`

**Content** :
```json
{
  "key": "[valid ECDH public key]"
}
```

#### Error Response
**Code** : `400 BAD REQUEST`

### Put Data

**URL** : `/putdata/<idD>`
**Method** : `POST`
**Data constraints**: Any valid JSON
```json
{}
```
#### Success Response
**Code** : `204 NO CONTENT`

#### Error Response
**Code** : `400 BAD REQUEST`


### Get Data

**URL** : `/getdata/<idD>`
**Method** : `GET`

#### Success Response
**Code** : `200 OK`

**Content** : The previous stored JSON
```json
{}
```

#### Error Response
**Code** : `400 BAD REQUEST`

## Deploy

Run the following steps to deploy the server:

```python
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```
