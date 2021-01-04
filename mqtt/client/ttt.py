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

key = bytes.fromhex('5b8f3a45d9fd18cde04ce43d9ac22ee9')
iv = bytes.fromhex('9e446718a6d037f5b19e417d5dc0130d')
plaintext = bytes.fromhex('000e00e0a000e0023044000000d00000610864260000e0000e0010160413')

print('Session key: {}'.format(key))
print('IV: {}'.format(iv))
print('Plaintext: {}'.format(plaintext))
#print(encrypt(key, iv, plaintext))
#ciphertext = encrypt(key, iv, plaintext)
ciphertext = bytes.fromhex('48bd56452c42cc7062b4e03c7c063eb2cc099e21e434f852eb0bf41a7e0b5172f502478ccb015b3c592ea4e5a9f87401c189d44b837e2f0b64483f8c10faf08f')
print(ciphertext)
print(decrypt(key, iv, ciphertext).decode('ascii'))