from .crypto import Crypto
from Crypto.Cipher import AES
import os
import hashlib
import base64

class Auth:
    def __init__(self, login, password):
        self.login = login
        self.password = password
    
    def pad(self, text):
        while len(text) % 16 != 0:
            text += b' '
        return text

    def sign_in(self, logins, passwords, salts):
        if self.login in logins:
            salt = salts[logins.index(self.login)]
            password = hashlib.pbkdf2_hmac(
                'sha256',
                self.password.encode('utf-8'),
                base64.b64decode(salt.encode("utf-8")), 
                100000
            )
            if base64.b64encode(password).decode("utf-8") == passwords[logins.index(self.login)]:
                return logins.index(self.login)
        return None

    def sign_up(self):
        crypto = Crypto()
        publickey, privatekey = crypto.gen_keys()

        salt = os.urandom(32)
        password = hashlib.pbkdf2_hmac(
            'sha256',
            self.password.encode('utf-8'),
            salt, 
            100000
        )
        aes = AES.new(self.pad(self.password.encode("utf-8")), AES.MODE_ECB)
        privatekey = base64.b64encode(aes.encrypt(self.pad(base64.b64decode(privatekey)))).decode("utf-8")
        publickey = publickey.decode("utf-8")
        return publickey, privatekey, base64.b64encode(salt).decode("utf-8"), base64.b64encode(password).decode("utf-8")