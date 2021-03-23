from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import base64
import textwrap

class Crypto:
    def __init__(self, publickey=None, privatekey=None):
        if publickey != None:
            self.publickey = RSA.importKey(base64.b64decode(publickey))
        if privatekey != None:    
            self.privatekey = RSA.importKey(base64.b64decode(privatekey))

    def gen_keys(self):
        self.privatekey = RSA.generate(2048)
        self.publickey = self.privatekey.publickey()
        return base64.b64encode(self.publickey.exportKey('PEM')), base64.b64encode(self.privatekey.exportKey('PEM'))

    def encrypt(self, text, key):
        if key == 'public':
            cipherrsa = PKCS1_OAEP.new(self.publickey)
        elif key == 'private':
            cipherrsa = PKCS1_OAEP.new(self.privatekey)
        text_parts = textwrap.wrap(text.decode("utf-8"), 16)
        encrypted_text = list(map(lambda x: base64.b64encode(cipherrsa.encrypt(x.encode("utf-8"))).decode("utf-8"), text_parts))
        return " ".join(encrypted_text)

    def decrypt(self, text, key):
        if key == 'public':
            cipherrsa = PKCS1_OAEP.new(self.publickey)
        elif key == 'private':
            cipherrsa = PKCS1_OAEP.new(self.privatekey)
        text_parts = text.split()
        decrypted_text = list(map(lambda x: cipherrsa.decrypt(base64.b64decode(x.encode("utf-8"))).decode("utf-8"), text_parts))
        return "".join(decrypted_text)