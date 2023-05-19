# vehicleforensics_evaluate

## Steps
1. After finish cloning the repo, their are two scripts(`producer.py` & `consuner.py`) for you to run.
2. Run `producer.py`, it is the encryption code for the `data/txt/original.txt`.
3. You will get `ciphertext_en.txt` & `ciphertext_epolys.txt` & `signature.txt` inside this folder `data/txt/`.
4. Run `comsumer.py`, it use ntru to decrypt the ciphertext(require these two files`ciphertext_en.txt` & `ciphertext_epolys.txt`).
5. You will get `result_plaintext.txt`, then you can make sure is the content same as `original.txt`.
6. Have to verify the signature. (still need to update).
7. Add feature for automatically reading mutiple data in the folder.(have to seperate different txt files into different folders(categories) first). 

## TO DO
1. Verify the signature.
> 5/20 complete
2. add feature for automatically reading mutiple data.
3. seperate different txt files into different folders(categories) -> sort each value into a json file.
4. add logging library to replace print... and record the result.


| Column 1 | Column 2 | Column 3 |
| -------- | -------- | -------- |
| Text     | Text     | Text     |
