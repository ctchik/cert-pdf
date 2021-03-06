import io
import os
import re
import csv
import sys
import glob
import time
import json
import fcntl
import base64
import shutil
import hashlib
import logging
import requests
import configparser
import tqdm

from btc_api_helpers import *

from path_helpers import *

from cert_tools import create_v2_certificate_template as tpl
from cert_tools import instantiate_v2_certificate_batch as ist

from cert_issuer import issue_certificates as isu
from cert_issuer import config

from vars import *

def start(export_path):
    os.makedirs(export_path, exist_ok = True)
    os.makedirs(get_summary_dir(), exist_ok = True)
    os.makedirs(get_work_dir(TOKEN), exist_ok = True)
    os.makedirs(get_unsigned_cert_dir(TOKEN), exist_ok = True)
    os.makedirs(get_template_dir(TOKEN), exist_ok = True)
    os.makedirs(get_roster_dir(TOKEN), exist_ok = True)
    os.makedirs(get_signed_cert_dir(TOKEN), exist_ok = True)
    os.makedirs(get_temp_input_dir(TOKEN), exist_ok = True)
    shutil.copyfile(get_tools_conf_template_dir(), get_tools_conf_dir(TOKEN))
    shutil.copyfile(get_issuer_conf_template_dir(), get_issuer_conf_dir(TOKEN))
    shutil.copytree(get_image_template_dir(), get_image_dir(TOKEN))

def modify_conf(pubkey, psw_file):
    psw_file = os.path.abspath(psw_file)
    modify_ini(get_tools_conf_dir(TOKEN), 'TEMPLATE', 'data_dir', get_conf_dir(TOKEN))
    modify_ini(get_tools_conf_dir(TOKEN), 'ISSUER', 'issuer_public_key', 'ecdsa-koblitz-pubkey:' + pubkey)
    modify_ini(get_issuer_conf_dir(TOKEN), 'ISSUERINFO', 'usb_name', os.path.split(psw_file)[0])
    modify_ini(get_issuer_conf_dir(TOKEN), 'ISSUERINFO', 'key_file', os.path.split(psw_file)[1])
    modify_ini(get_issuer_conf_dir(TOKEN), 'ISSUERINFO', 'issuing_address', pubkey)
    modify_ini(get_issuer_conf_dir(TOKEN), 'ISSUERINFO', 'work_dir', get_work_dir(TOKEN))
    modify_ini(get_issuer_conf_dir(TOKEN), 'ISSUERINFO', 'unsigned_certificates_dir', get_unsigned_cert_dir(TOKEN))
    modify_ini(get_issuer_conf_dir(TOKEN), 'ISSUERINFO', 'blockchain_certificates_dir', get_signed_cert_dir(TOKEN))
       
def transfer_input(import_path):
    files = os.listdir(import_path)
    with tqdm.tqdm(total = len(files)) as bar:
        for f in files:
            bar.update(1)
            shutil.move(os.path.join(import_path, f), get_temp_input_dir(TOKEN))

def clear(clear_all = False):
    if clear_all:
        shutil.rmtree(STAGE_DIR, ignore_errors = True)
    else:
        shutil.rmtree(get_conf_dir(TOKEN))
    
def getBase64(filename):
    file = open(filename, 'rb')
    file_read = file.read()
    file_encode = base64.encodebytes(file_read).decode('utf-8')
    return file_encode
    
def write_roster(list_FILENAME, list_FILECONTENT, export_file):
    headers = ['pubkey', 'name', 'identity', 'filename', 'filecontent']
    csvfile = open(export_file, 'w')
    writer = csv.DictWriter(csvfile, headers)
    writer.writeheader()
    
    with tqdm.tqdm(total = len(list_FILENAME)) as bar:
        for i in range(0, len(list_FILENAME)):
            writer.writerow({'pubkey': 'ecdsa-koblitz-pubkey:' + str(hashlib.sha256(b'dummy').hexdigest()),
                             'name': list_FILENAME[i][:11],
                             'identity': '',
                             'filename' : list_FILENAME[i],
                             'filecontent' : list_FILECONTENT[i]})
            bar.update(1)

def create_roster(import_path):
    extension_list = ['.pdf', '.htm', '.html']

    list_FILENAME = []
    list_FILECONTENT = []
    count = 0

    with tqdm.tqdm(total = len(glob.glob(os.path.join(import_path, '*.*')))) as bar:
        for filename in glob.glob(os.path.join(import_path, '*.*')):
            pr_name = os.path.split(filename)[1]
            pr, ext = os.path.splitext(pr_name)
            if ext not in extension_list:
                continue
            list_FILENAME.append(pr_name)
            list_FILECONTENT.append(getBase64(filename))
            count = count + 1
            bar.update(1)

    write_roster(list_FILENAME, list_FILECONTENT, get_roster_file_dir(TOKEN))

    return count

def create_template():
    conf = tpl.get_config(get_tools_conf_dir(TOKEN))
    tpl.create_certificate_template(conf)

def create_certificates():
    conf = ist.get_config(get_tools_conf_dir(TOKEN))
    ist.create_unsigned_certificates_from_roster(conf)

def config_logger():
    logging.basicConfig(filename = get_stage_log_dir(TOKEN), filemode = 'a', format = '[%(asctime)s] %(message)s', datefmt = '%Y-%m-%d %H:%M:%S')
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter("%(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

def issue_certificates(pubkey):
    config_logger()

    print()
    logging.info('Trying to acquire file lock ...')
    
    bypass = False

    file = open(get_latest_transaction_file_dir(), 'r+')
    fcntl.flock(file.fileno(), fcntl.LOCK_EX)
    logging.info('Lock acquired ...')
    
    tx_id = ''
    successful = False
    latest_transaction = file.readline()
    chain_latest = ''

    count = 0

    if latest_transaction == '':
        bypass = True

    if bypass:
        logging.info('The latest transaction check is bypassed ...')
    else:
        logging.info('Waiting the latest transaction to be confirmed ...')
        while get_confirmation(latest_transaction, TOKEN) == 0:
            logging.info('No confirmation yet. Will retry ...')
            count += 1
            if count >= 1000: # timeout
                file.close()
                raise Exception('Waiting timeout.')
            request_sleep(TOKEN)
        count = 0
        while True:
            count += 1
            chain_latest = get_latest_transaction(pubkey, TOKEN)
            if chain_latest != 'retry':
                break
            if count >= 1000:
                file.close()
                raise Exception('Waiting timeout.')
            request_sleep(TOKEN)
        logging.info('Passed')

    if chain_latest in latest_transaction or bypass:
        if not bypass:
            logging.info('Latest transaction authenticity check passed ...')
        try:
            parsed_config = config.get_config(get_issuer_conf_dir(TOKEN))
            tx_id = isu.main(parsed_config)
            if tx_id:
                logging.info('Transaction id is %s', tx_id)
                file.seek(0)
                file.write(tx_id)
                successful = True
            else:
                logging.error('Certificate issuing failed')
                file.close()
        except Exception as ex:
            logging.error(ex, exc_info = True)
            file.close()
            return [tx_id, successful]
    else:
        logging.error('Latest transaction authenticity check failed ... The public key is possibly stolen by someone else, please change a public key.')
        file.close()

    return [tx_id, successful, file]

def wait(tx_id, file):
    timeout = 1000 # in min
    for i in range(timeout):
        if get_confirmation(tx_id, TOKEN) > 0:
            file.close()
            logging.info('Passed')
            return
        logging.info('No confirmation yet. Will retry ...')
        request_sleep(TOKEN)
    file.close()
    raise Exception('Waiting timeout.')

def generate_summary(export_path):
    output = dict()
    with tqdm.tqdm(total = len(glob.glob(os.path.join(get_signed_cert_dir(TOKEN), '*.json'))) + 1) as bar:
        for filename in glob.glob(os.path.join(get_signed_cert_dir(TOKEN), '*.json')):
            with open(filename, 'rb') as f:
                data = json.load(f)
                identity = data['recipient']['identity']
                id = data['id']
                issuedtime = data['issuedOn']
                usr = dict()
                usr['cert_id'] = id
                usr['issued_time'] = issuedtime
                origin_filename, _ = os.path.splitext(data['filename'])
                output[identity] = usr
            shutil.copy(filename, os.path.join(export_path, origin_filename + id.replace('urn:uuid:', '') + '.json'))
            bar.update(1)
        with open(get_summary_file_dir(TOKEN), 'w') as f:
            json.dump(output, f, indent = 4)
        bar.update(1)
    print('Summary has been written to ' + get_summary_file_dir(TOKEN))
