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

3. Because of feature 2, when multiple callings are in process simultenously, only one calling can successfully get into the issuing phase. This feature is implemented by adding a file lock onto the local latest transaction file.

4. Each calling will be assigned with a job ID, which is a uuid4. Job log of each calling will be produced. 

## Configuration

### 1. Configure `.cert_pdf`

This configuration mimics the way that Emacs uses. Please first create a file named `.cert_pdf` under the `Home` directory (e.g., in Linux, please create `~/.cert_pdf`) with the content of the one in the repo.

```
$ sudo cp .cert_pdf ~/.cert_pdf
```

By default, you don't need to modify the content of this file. If you use the default setting, all files related to cert-pdf will be stored in `root_dir`.

### 2. Configure the `configuration/issuer_conf_template.ini` and `configuration/tools_conf_template.ini`

Please don't modify any entry which says `[INTENDED TO BE BLANK]`. In `tools_conf_template.ini`, please remain the sections `IMAGES`, `TEMPLATE`, `INSATNTIATE` and `OTHER` unchanged.

### 3. Move the 2 files to the working directory

Here we assume that the `issuer_conf` and `tools_conf` in `.cert_pdf` are `templates/issuer_conf_template.ini` and `templates/tools_conf_template.ini` respectively, with `/Users/PPFish/pdf_cert_conf` as `root_dir`. Then run

```
$ sudo mkdir -p /Users/PPFish/pdf_cert_conf/templates
$ sudo cp configuration/issuer_conf_template.ini /Users/PPFish/pdf_cert_conf/templates/issuer_conf_template.ini
$ sudo cp configuration/tools_conf_template.ini /Users/PPFish/pdf_cert_conf/templates/tools_conf_template.ini
``` 

### 4. Move certificate images to the working directory

Here we assume that the `image_dir` in `.cert_pdf` is `images`, with `/Users/PPFish/pdf_cert_conf` as `root_dir`. Then run

```
$ sudo cp -R configuration/images /Users/PPFish/pdf_cert_conf/images
```

### 5. Create a blank latest_transaction file to bypass the latest transaction check

```
$ sudo touch /Users/PPFish/pdf_cert_conf/latest_transaction.txt
```

## Usage

### Issue a batch of PDF files

```
python api.py issue --import_path IMPORT_PATH
                    --export_path EXPORT_PATH
                    --pubkey PUBKEY
                    --psw_file PSW_FILE
                    [--itsc ITSC]
                    [--name_pattern NAME_PATTERN]
                    [--clear_input]

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
      
--clear_input
      if this tag is typed, the script will clean up the import directory upon execution
```

### Extract the PDF file inside a certificate

```
python api.py extract --cert_path CERT_PATH
                      --export_path EXPORT_PATH

Argument details:

--cert_path CERT_PATH
      the file location of the cert (json file)

--export_path EXPORT_PATH
      the export location of the PDF file
```

### Verify a certificate

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

### Clean cache directory

```
python api.py clean
```

## Acknowledgement

Thank [Blockcerts](https://github.com/blockchain-certificates) for providing the core components `cert-tools`, `cert-issuer` and `cert-verifier` of this project

Information of transaction is provided by API [blockcypher.com](blockcypher.com).
