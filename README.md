# vehicleforensics_evaluate

## Steps
1. After finish cloning the repo, their are two scripts(`producer.py` & `consuner.py`) for you to run.
1. Run `producer.py`, it is the encryption code for the `data/txt/original.txt`.
1. You will get `ciphertext_en.txt` & `ciphertext_epolys.txt` & `signature.txt` inside this folder `data/txt/`.
1. Run `comsumer.py`, it use ntru to decrypt the ciphertext(require these two files`ciphertext_en.txt` & `ciphertext_epolys.txt`).
1. You will get `result_plaintext.txt`, then you can make sure is the content same as `original.txt`.
1. Have to verify the signature. (still need to update).
1. Add feature for automatically reading mutiple data in the folder.(have to seperate different txt files into different folders(categories) first). 
1. Remember to decode the resut plaintext to get the `string` type of string.

## TO DO
1. Verify the signature.
> 5/20 complete
1. add feature for automatically reading mutiple data.
> 10/17 done
1. seperate different txt files into different folders(categories)
> 10/17 done
1. sort each value into a json file.(reduce the txt files and make all of the information in one)
1. add logging library to replace print... and record the result.(using `from absl import logging`)
1. add a for loop for glob
1. remove processed file. (os.remove(file_path))