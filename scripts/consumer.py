from hashlib import sha3_256
import hashlib

from falcon_utils import falcon

from ntru_utils.NtruEncrypt import *
from ntru_utils.Polynomial import Zx
from ntru_utils.num_to_polynomial import *

from config import *


TEST_N = 1

path=r'.\data\txt'

class data_encoding():
    def __init__(self):
        self.CFSK_f = F_f
        self.CFSK_g = F_g
        self.CFSK_N = F_N
        self.CFSK = falcon.SecretKey(self.CFSK_N, self.CFSK_f, self.CFSK_g)
        self.CFPK = falcon.PublicKey(F_N, F_h)
        self.SNPK, self.SNSK = generate_keypair(N_P, N_Q, N_D, N_N)
        self.salt = HASH_SALT
        
    def ntruTrans(self, message):
        characterPolynomials, N = koblitz_encoder(
            message, N_elliptic_a, N_elliptic_b)
        return characterPolynomials, N


    def ntruEncrypt(self, message):
        # print(f"{type(message)} -> {message}")
        characterPolynomials, N = self.ntruTrans(message)
        cipher_polys = []
        for element in characterPolynomials:
            cipher_text = encrypt(element, self.SNPK, N_D, N, N_Q)
            cipher_polys.append(cipher_text)
        return cipher_polys, N


    def ntruDecrypt(self, cipherPolys, n):
        dec_w = []
        for element in cipherPolys:
            decrypted_message = decrypt(element, self.SNSK, N_P, N_Q, n)
            # print(decrypted_message.print_polynomial())
            dec_w.append(decrypted_message.coeffs)
        decrypted_plain_text = koblitz_decoder(points_decoder(dec_w))
        # print(decrypted_plain_text)
        return decrypted_plain_text
        
    def hashMessage(self, message):
        # salt = os.urandom(32)
        key = hashlib.pbkdf2_hmac(
            'sha256', # The hash digest algorithm for HMAC
            message.encode('utf-8'), # Convert the password to bytes
            self.salt, # Provide the salt
            100000 # It is recommended to use at least 100,000 iterations of SHA-256 
            # dklen=128 # Get a 128 byte key
        )
        return self.salt + key   


def main():
    data_encoing = data_encoding()

    i = 0

    plainTextList = []
    
    while i < TEST_N:
        with open(f'{path}/ciphertext_epolys.txt', 'r') as f:
            sm = eval(f.read())

        with open(f'{path}/ciphertext_en.txt', 'r') as f:
            n = int(f.read())
        
        # decrypto
        cipher = []
        for j in sm:
            cipher.append(Zx(j)) 
        plainText = data_encoing.ntruDecrypt(cipher, n)
        plainTextList.append([plainText.encode('utf-8')])

        with open(f'{path}/result_plaintext.txt', 'w') as f:
            f.write(str(plainTextList))
    
        i += 1

if __name__ == '__main__':
    main()
