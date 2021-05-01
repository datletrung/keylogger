import base64
import random

class VigenereCipher(object):
    def __init__(self, alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~ '):
        self.alphabet = alphabet
    
    def generate_key(self):
        key_list = list(self.alphabet)
        random.shuffle(key_list)
        return ''.join(key_list)
        
    def encrypt(self, plaintext, key):
        try:
            key = base64.urlsafe_b64decode(key).decode()
        except:
            print('Invalid key')
            return False
        key_length = len(key)
        key_as_int = [ord(i) for i in key]
        plaintext_int = [ord(i) for i in plaintext]
        ciphertext = ''
        for i in range(len(plaintext_int)):
            value = (plaintext_int[i] - 32 + key_as_int[i % key_length]) % len(self.alphabet)
            ciphertext += chr(value + 32)
        ciphertext = base64.urlsafe_b64encode(ciphertext.encode()).decode()
        return ciphertext

    def decrypt(self, ciphertext, key):
        try:
            key = base64.urlsafe_b64decode(key).decode()
        except:
            print('Invalid key')
            return False
        ciphertext = base64.urlsafe_b64decode(ciphertext).decode()
        key_length = len(key)
        key_as_int = [ord(i) for i in key]
        ciphertext_int = [ord(i) for i in ciphertext]
        plaintext = ''
        for i in range(len(ciphertext_int)):
            value = (ciphertext_int[i] - 32 - key_as_int[i % key_length]) % len(self.alphabet)
            plaintext += chr(value + 32)
        return plaintext

s = 'ah94ghunav981 47!^@#46^$!)WEGPADS@gmail!#$%^&*()_+|"{P:.com'
alphabet = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~ '

v = VigenereCipher(alphabet)

key = base64.urlsafe_b64encode(v.generate_key().encode()).decode()
#print('Key:', key)

encode_s = v.encrypt(s, key)
decode_s = v.decrypt(encode_s, key)

print('Encoded:', encode_s)
print('Decoded:', decode_s)

