# cert-pdf
This is a variant of Blockcert which enables users to embed PDF files inside blockcerts and deploy them on the blockchain.

## Install

1. Please make sure that you have the recommended [python environment](https://github.com/blockchain-certificates/cert-issuer/blob/master/docs/virtualenv.md) to run the blockcert project.

2. Install the **modified** blockcert modules via following commands:

```
git clone https://github.com/ppfish45/cert-tools.git && cd cert-tools && sudo pip install . && cd ../
git clone https://github.com/ppfish45/cert-issuer.git && cd cert-issuer && sudo pip install . && cd ../
git clone https://github.com/ppfish45/cert-verifier.git && cd cert-verifier && sudo pip install . && cd ../
```

3. Clone cert-pdf and enter the directory

```
git clone https://github.com/ppfish45/cert-pdf.git && cd cert-pdf
```

<<<<<<< HEAD
=======
4. Clone cert-pdf and enter the directory

```
$ git clone https://github.com/ppfish45/cert-pdf.git && cd cert-pdf
```

## New Features

1. The api supports concurrent calling. Each calling will create a staging folder where working files will be temporarily stored.

2. Will compare the local latest transaction and the online latest transaction before issuing a batch of PDF files. It prevents the occurrence of fake certificates when the private key is stolen by someone else. 

3. Because of feature 2, when multiple callings are in process simultenously, only one calling can successfully get into the issuing phase. This feature is implemented by adding a file lock onto the local latest transaction file.

4. Each calling will be assigned with a job ID, which is a uuid4. Job log of each calling will be produced. 

## Configuration

### 1. Configure `.cert_pdf`

This configuration mimics the way that Emacs uses. Please first create a file named `.cert_pdf` under the `Home` directory (e.g., in Linux, please create `~/.cert_pdf`) with the content of the one in the repo.

```
$ sudo cp cert-pdf/.cert_pdf ~/.cert_pdf
```

By default, you don't need to modify the content of this file. If you use the default setting, all files related to cert-pdf will be stored in `root_dir`.

### 2. Configure the `issuer_conf_template.ini` and `tools_conf_template.ini`

Please don't modify any entry which says `[INTENDED TO BE BLANK]`. In `tools_conf_template.ini`, please remain the sections `IMAGES`, `TEMPLATE`, `INSATNTIATE` and `OTHER` unchanged.

>>>>>>> 5674a074693774558bc3afa5bf5b9172dac5286e
## Usage

### Issue a batch of PDF files

1. Configure the issuer & blockchain account info in `configuration/cert_issuer_conf.ini` and `configuration/cert_tools_conf.ini`. Please do not modify the the directory related to `template`, `unsigned_certificates` and `roster`.

2. Import `cert_pdf/api.py` and run following code in python
  ``` 
  issue_batch(import_path, export_path, summary_path, name_pattern = '|DOCID|-|NAME|')
  ```

3. For details of parameters, please refer to `cert_pdf/api.py`

4. **NOTICE THAT THE BITCOIN TESTNET ACCOUNT USED IS ONLY FOR TEST. PLEASE MODIFY IT TO YOUR OWN'S.**

5. **THE PATHS OF IMAGES IN DIFFERENT OS MAY DIFFER, PLEASE MODIFY IT IN `configuration/cert_issuer_conf.ini` (IN `IMAGES` SECTION AND `issuer_signature_lines`).**

### Verify an Certificate

1. Import `cert_pdf/api.py` and run following code in python
  ``` 
  verify_cert(cert_path, pubkey_list)
  ```

2. Note that pubkey_list is list of valid public keys of the issuer.

3. This function will check 6 items of the cert.
```
   transaction is confirmed - passed
  issued by specific issuer - passed
 has not been tampered with - passed
            has not expired - passed
       has not been revoked - passed
        issuer authenticity - passed
```

### Extract the PDF File inside an Certificate

<<<<<<< HEAD
1. Import `cert_pdf/api.py` and run following code in python
  ``` 
  extract_pdf(cert_path, export_path)
  ```
=======
Information of transaction is provided by APIs of [btc.com](btc.com) (Bitcoin Mainnet) and [blockcypher.com](blockcypher.com) (Bitcoin Testnet).
>>>>>>> 5674a074693774558bc3afa5bf5b9172dac5286e
