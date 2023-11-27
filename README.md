# vehicleforensics_evaluate

## Steps
- Producer.py
    1. After finish cloning the repo, their are two scripts(`producer.py` & `consuner.py`) for you to run.
    1. You have to connect the data sender by using kvasar hardware to your device.
    1. Run `producer.py`, it is a data receive & sign & encrypt & uploading through sftp code.
    1. Get data line by line in this format`log_message = "{id:0>8X}  {dlc}  {data}  {current_time}"`, it will automatically sign(falcon) and encrypt(ntru) and upload through sftp in a file format.
    1. You may see 3 files named `ciphertext_en.txt` & `ciphertext_epolys.txt` & `signature.txt` under `.\data\Encrypt` folder.
    1. (optional) If you want to take a look at the files in local, you may comment out the `rmtree` and `os.mkdir` two lines, and you may see the results.
    1. After signature and encryption collecting from the device, it will automatically upload to server through sftp.
    1. Refresh server to take a look at the data.
    1. We store data in a folder way, the folder named `datetime.datetime.now().strftime("%Y-%m-%d-%H%M%S.%f")`, and inside you'll see those three files.
- Consumer.py
    1. Install this `consumer.py` into the server with monitering feature.
    1. Set path to relate path
    1. It will automatically scan all of the files from the main path, and decrypt `ciphertext_en.txt` & `ciphertext_epolys.txt` to get`result_plaintext.txt`.
    1. It will also verify through `Signature.txt` to check if the result signature is correct(same) or not.
    1. Remember to decode the resut plaintext to get the `string` type of string.

## TO DO
1. Install consumer into server
1. Seperate Falcon publicKey/privateKey and Ntru publicKey/privateKey in `producer.py` and `consumer.py`

# Additional
- Don't use SFTP for the value sending protocal, try to use another way like socket, HTTP....

## DKW(dont know why)
1. Maximum characters(You cannot sign or encrypt in a long string):
    ```bash
    000007DF  8  02 01 05 00 00 00 00 00  53          2023-08-31 15:52:56 
    000007E8  8  03 41 05 88 00 00 00 00  53          2023-08-31 15:52:56 
    000007DF  8  02 01 10 00 00 00 00 00  154          2023-08-31 15:52:57 
    000007E8  8  04 41 10 04 60 00 00 00  154          2023-08-31 15:52:57 
    ```
    - Hash + Encrpyt + Save/Load_file: Execution time: 0.20 seconds (On Raspberry pi)
    - Decrpyt + Verify + Save/Load_file: Execution time: 0.26 seconds (On Server)

    For hash output error: `Squared norm of signature is too large: *********`<br />
    For encrypt output error: `except: -1`(set by programmer)
