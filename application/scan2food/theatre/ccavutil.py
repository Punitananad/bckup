from Crypto.Cipher import AES
from hashlib import md5
import base64

def pad(data):
    length = 16 - (len(data) % 16)
    return data + chr(length) * length

def unpad(data):
    return data[:-ord(data[-1])]

def encrypt(plainText, workingKey):
    iv = bytes([i for i in range(16)])
    encDigest = md5(workingKey.encode('utf-8')).digest()
    plainText = pad(plainText)
    cipher = AES.new(encDigest, AES.MODE_CBC, iv)
    encryptedText = cipher.encrypt(plainText.encode('utf-8'))
    return encryptedText.hex()  # or use base64.b64encode(encryptedText).decode()

def decrypt(cipherText, workingKey):
    iv = bytes([i for i in range(16)])
    decDigest = md5(workingKey.encode('utf-8')).digest()
    encryptedBytes = bytes.fromhex(cipherText)
    cipher = AES.new(decDigest, AES.MODE_CBC, iv)
    decryptedText = cipher.decrypt(encryptedBytes).decode('utf-8')
    return unpad(decryptedText)
