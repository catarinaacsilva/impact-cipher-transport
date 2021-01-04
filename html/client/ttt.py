# coding: utf-8

__author__ = 'Catarina Silva'
__version__ = '0.1'
__email__ = 'c.alexandracorreia@av.it.pt'
__status__ = 'Development'


from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


def encrypt(key, iv, plaintext):
    encryptor = Cipher(algorithms.AES(key), modes.CTR(iv)).encryptor()
    return encryptor.update(plaintext) + encryptor.finalize()


def decrypt(key, iv, ciphertext):
    decryptor = Cipher(algorithms.AES(key), modes.CTR(iv)).decryptor()
    return decryptor.update(ciphertext) + decryptor.finalize()

key = bytes.fromhex('6a52e16ce88fd6a54c9c38dba4b4ca3b85618d8fad8493fc')
iv = bytes.fromhex('5a5cfbcab5f2dc518ac85025a5cf80b8')
#plaintext = bytes.fromhex('000e00e0a000e0023044000000d00000610864260000e0000e0010160413')

#print('Session key: {}'.format(key))
#print('IV: {}'.format(iv))
#print('Plaintext: {}'.format(plaintext))
#print(encrypt(key, iv, plaintext))
#ciphertext = encrypt(key, iv, plaintext)
ciphertext = bytes.fromhex('70a1a15f9b0ec90b6bed7c0bec34bf7ddb5e243e67c6cebf33a90cababc3c2cf9e853d8c4c2f6364f7630f2262a1d46400ac76d8e28c8ee1e3c6cf3d33306621')
plain = decrypt(key, iv, ciphertext)
print(plain.decode('ascii'))