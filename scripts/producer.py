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
import time

import sys
from canlib import canlib
import paramiko
import shutil

class sftp_connect():
    def __init__(self):
        self.local_dir_path = r"C:\Users\BKMY\Desktop\raw_data\vehicleforensics_evaluate-master\data\Encrypt"
        self.remote_dir_path = '/home/project/vehicle/raw_data/'  

        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh_client.connect(HOSTNAME,1090, USERNAME, PASSWORD)

        self.sftp_client = self.ssh_client.open_sftp()

    def sftp(self):
        try:
            with self.ssh_client.open_sftp() as sftp:
                if not os.path.exists(self.local_dir_path):
                    print("本地端檔案不存在！")
                    return

                try:
                    sftp.stat(self.remote_dir_path)
                except IOError:
                    sftp.mkdir(self.remote_dir_path)

            for root, dirs, files in os.walk(self.local_dir_path):
                for file in files:
                    local_file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(local_file_path, self.local_dir_path)
                    remote_file_path = os.path.join(self.remote_dir_path, relative_path).replace("\\", "/")
                    self.sftp_client.put(local_file_path, remote_file_path)

                for dir_ in dirs:
                    local_dir = os.path.join(root, dir_)
                    relative_path = os.path.relpath(local_dir, self.local_dir_path)
                    remote_dir = os.path.join(self.remote_dir_path, relative_path).replace("\\", "/")

                    try:
                        self.sftp_client.mkdir(remote_dir)
                    except IOError:
                        pass
            print("-----上傳檔案成功!-----")

        except Exception as e:
            print("upload error: ", e)
        finally:
            # delete files in local_dir_path
            shutil.rmtree(self.local_dir_path)  
            os.mkdir(self.local_dir_path)  
            self.sftp_client.close()

        self.ssh_client.close()


class raw_data():
    def __init__(self):
        # start_time = time.time()

        self.channel_number = 0

        self.get_chdata()

    def get_chdata(self):
        # Specific CANlib channel number may be specified as the first argument
        if len(sys.argv) == 2:
            channel_number = int(sys.argv[1])

        chdata = canlib.ChannelData(channel_number)
        print("%d. %s (%s / %s)" % (channel_number, chdata.channel_name,
                                    chdata.card_upc_no,
                                    chdata.card_serial_no))

        # Open CAN channel, virtual channels are considered okay to use
        ch = canlib.openChannel(channel_number, canlib.canOPEN_ACCEPT_VIRTUAL)

        print("Setting bitrate to 500 kb/s")
        ch.setBusParams(canlib.canBITRATE_500K)
        ch.busOn()

        # Start listening for messages
        finished = False
        while not finished:
            try:
                frame = ch.read(timeout=50)
                self.print_frame(frame)
            except (canlib.canNoMsg):
                pass
            except (canlib.canError) as ex:
                print(ex)
                finished = True

        # Channel teardown
        ch.busOff()
        ch.close()

    def print_frame(frame):
        """Prints a message to screen and logs it to the specified file"""
        current_time = datetime.datetime.now().strftime("%Y-%m-%d-%H%M%S.%f")
        if (frame.flags & canlib.canMSG_ERROR_FRAME != 0):
            log_message = "***ERROR FRAME RECEIVED***"
        else:
            # log_message = "{id:0>8X}  {dlc}  {data}  {timestamp}          {current_time}".format(
            log_message = "{id:0>8X}  {dlc}  {data}  {current_time}".format(
                id=frame.id,
                dlc=frame.dlc,
                data=' '.join('%02x' % i for i in frame.data),
                # timestamp=frame.timestamp,
                current_time=current_time
            )
        log_message = log_message.upper()
        print(log_message)

        Signature_Encryption.sign_encrypt(log_message)

        sftp_connect()
 
        # Calculate run time
        # end_time = time.time()
        # execution_time = end_time - start_time
        # print("Execution time: {:.2f} seconds".format(execution_time))
 
        time.sleep(1)


class Signature_Encryption():
    def __init__(self, log_msg) -> None:
        data_path = Path('./data/')
        self.data_encoing = data_encoding()
        self.result_dir = Path(data_path, 'Encrypt', datetime.datetime.now().strftime("%Y-%m-%d-%H%M%S.%f"))
        self.log_msg = log_msg


    def sign_encrypt(self):
        self.result_dir.mkdir(parents=True, exist_ok=True)

        self.message_str = self.log_msg
        self.message_byt = self.message_str.encode()

        # hash
        h_o = sha3_256()
        h_o.update(self.message_byt)
        h_byt = h_o.digest()

        # sign
        s_byt = self.data_encoing.CFSK.sign(h_byt)
        with open(self.result_dir / 'signature.txt', 'w') as f:
            f.write(str(s_byt))

        # encrypt
        e_polys, e_n = self.data_encoing.ntruEncrypt(self.message_str)
        e_list = []
        for e_poly in e_polys:
            e_list.append(e_poly.coeffs)

        with open(self.result_dir / 'ciphertext_epolys.txt', 'w') as f:
            f.write(str(e_list))

        with open(self.result_dir / 'ciphertext_en.txt', 'w') as f:
            f.write(str(e_n))


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
    raw_data()


if __name__ == '__main__':
    main()