import sys,os
sys.path.append(os.getcwd())
import glob
from pathlib import Path
import datetime
# from absl import logging

from hashlib import sha3_256
import hashlib

from falcon_utils import falcon

from ntru_utils.NtruEncrypt import *
from ntru_utils.Polynomial import Zx
from ntru_utils.num_to_polynomial import *

from config import * 


data_path=Path('./data/txt')


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

    txt_path = data_path / 'text'
    txt_files = glob.iglob(os.path.join(txt_path / '*.txt'))

    for file_path in txt_files:
        print(file_path)
        result_dir = Path(data_path, datetime.datetime.now().strftime("%Y-%m-%d-%H%M%S.%f"))
        print(result_dir)
        result_dir.mkdir(parents=True, exist_ok=True)

        with open(file_path, 'r') as f: # 純str
            m_str = f.read()

        m_byt = m_str.encode()

        # hash
        h_o = sha3_256()
        h_o.update(m_byt)
        h_byt = h_o.digest()

        # sign
        s_byt = data_encoing.CFSK.sign(h_byt)

        # os.remove(file_path)

        with open(result_dir / 'signature.txt', 'w') as f:
            f.write(str(s_byt))

        # encrypt
        e_polys, e_n = data_encoing.ntruEncrypt(m_str)


        e_list = []
        for e_poly in e_polys:
            e_list.append(e_poly.coeffs)


        with open(result_dir / 'ciphertext_epolys.txt', 'w') as f:
            f.write(str(e_list))

        with open(result_dir / 'ciphertext_en.txt', 'w') as f:
            f.write(str(e_n))


if __name__ == '__main__':
    main()