# cert-pdf
This is a variant of Blockcert which enables users to embed PDF files inside blockcerts and deploy them on the blockchain.

## Install

1. Please make sure that you have the recommended [python environment](https://github.com/blockchain-certificates/cert-issuer/blob/master/docs/virtualenv.md) to run the blockcert project.

2. Install the **modified** blockcert module via following commands:

```
$ git clone https://github.com/ppfish45/cert-tools.git && cd cert-tools && sudo pip install . && cd ../
$ git clone https://github.com/ppfish45/cert-issuer.git && cd cert-issuer && sudo pip install . && cd ../
$ git clone https://github.com/ppfish45/cert-verifier.git && cd cert-verifier && sudo pip install . && cd ../
```

3. Install `tqdm` for UI of the api

```
$ pip install tqdm
```

4. Clone cert-pdf and enter the directory

```
$ git clone https://github.com/ppfish45/cert-pdf.git && cd cert-pdf
```

## New Features

1. The api supports concurrent calling. Each calling will create a staging folder where working files will be temporarily stored.

2. Will compare the local latest transaction and the online latest transaction before issuing a batch of PDF files. It prevents the occurrence of fake certificates when the private key is stolen by someone else. 

3. Because of feature 2, when multiple callings are in process simultenously, only one calling can successfully get into the issuing phase. This feature is implemented by adding a file lock onto the local latest transaction file.

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

## Usage

### 1. Issue a Batch of PDF Files

```
python api.py issue --import_path IMPORT_PATH
                    --export_path EXPORT_PATH
                    --pubkey PUBKEY
                    --psw_file PSW_FILE
                    [--itsc ITSC]
                    [--name_pattern NAME_PATTERN]

Args that is enclosed by [] is optional.

Argument details:

--import_path IMPORT_PATH
      the directory where all PDFs are stored which need to be issued

--export_path EXPORT_PATH
      the destination of the issued certs (json files)

--pubkey PUBKEY
      the public key (bitcoin address) used for this issuing

--psw_file PSW_FILE
      the location of the file where the private key is stored

--itsc ITSC
      additional information, the itsc account of thhe owner of this calling （default: None)

--name_pattern NAME_PATTERN
      the formation of filename where |NAME| and |DOCID| are wildcards to match the corresponding info. PLAESE DON'T include '.pdf' in name_pattern. (default: '|DOCID|-|NAME|')
```

### 2. Extract the PDF File inside a Certificate

```
python api.py extract --cert_path CERT_PATH
                      --export_path EXPORT_PATH

Argument details:

--cert_path CERT_PATH
      the file location of the cert (json file)

--export_path EXPORT_PATH
      the export location of the PDF file
```

### 3. Verify a Certificate

```
python api.py verify --cert_path CERT_PATH
                     --pubkey_list PUBKEY_LIST

Argument details:

--cert_path CERT_PATH
      the location of the cert file

--pubkey_list PUBKEY_LIST
      a valid (or 'official') list of public keys, namely, only the certs with a public key which is contained in this list will be regard as valid (e.g., '--pubkey_list 123,234,345')
```

The return value of this function will be a json which tells the result of verification, e.g.,

```
[
  {'name': 'transaction is confirmed', 'passed': True},
  {'name': 'issued by specific issuer', 'passed': True},
  {'name': 'has not been tampered with', 'passed': True},
  {'name': 'has not expired', 'passed': True},
  {'name': 'has not been revoked', 'passed': True},
  {'name': 'issuer authenticity', 'passed': True},
  {'name': '*OVERALL VALIDATION', 'passed': True}
]
```

## Acknowledgement

Thank [Blockcerts](https://github.com/blockchain-certificates) for providing the core components `cert-tools`, `cert-issuer` and `cert-verifier` of this project

Information of transaction is provided by APIs of [btc.com](btc.com) (Bitcoin Mainnet) and [blockcypher.com](blockcypher.com) (Bitcoin Testnet).