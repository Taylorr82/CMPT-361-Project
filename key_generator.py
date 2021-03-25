from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad

def make_keypair(modulus_length):
        key = RSA.generate(modulus_length)
        pub_key = key.publickey()
        private_key = key.exportKey('PEM')
        public_key = pub_key.exportKey('PEM')
        return private_key, public_key

def store_key(location, key):
    store = open(location, "wb")
    store.write(key)
    store.close()

def generate_client_keys():

    modulus_length = 2048

    for i in range (1,6):
        private_key, public_key = make_keypair(modulus_length)
        
        store_key("client/client{}_private.pem".format(i), private_key)
        store_key("client/client{}_public.pem".format(i), public_key)
        store_key("server/client{}_public.pem".format(i), public_key)

def generate_server_keys():

        modulus_length = 2048

        private_key, public_key = make_keypair(modulus_length)
        
        store_key("server/server_private.pem", private_key)
        store_key("client/server_public.pem", public_key)
        store_key("server/server_public.pem", public_key)

generate_client_keys()
generate_server_keys()