import os
import re
import csv
import sys
import glob
import json
import base64
import shutil
import hashlib
import logging
import configparser

from cert_tools import create_v2_certificate_template as tpl
from cert_tools import instantiate_v2_certificate_batch as ist

from cert_issuer import issue_certificates as isu
from cert_issuer import config

dirname = os.path.split(os.path.split(os.path.abspath(__file__))[0])[0]
conf_dir = os.path.join(dirname, 'configuration')
unsigned_cert_dir = os.path.join(conf_dir, 'unsigned_certificates')
templates_dir = os.path.join(conf_dir, 'templates')
roster_dir = os.path.join(conf_dir, 'roster', 'roster.csv')
issuer_conf_dir = os.path.join(conf_dir, 'cert_issuer_conf.ini')
tools_conf_dir = os.path.join(conf_dir, 'cert_tools_conf.ini')
work_dir = os.path.join(conf_dir, 'work')

# clean the temp dir

def clear():
    shutil.rmtree(unsigned_cert_dir)
    shutil.rmtree(templates_dir)
    os.makedirs(unsigned_cert_dir)
    os.makedirs(templates_dir)

def getBase64(filename):
    file = open(filename, 'rb')
    file_read = file.read()
    file_encode = base64.encodebytes(file_read).decode('utf-8')
    return file_encode

def modify_ini(ini_file, section, key, new_value):
    config = configparser.RawConfigParser(allow_no_value = True)
    config.optionxform = str
    config.read(ini_file)
    config.set(section, key, new_value)
    with open(ini_file, "w") as output:
        config.write(output)

def modify_conf():
    print(issuer_conf_dir)
    modify_ini(tools_conf_dir, 'TEMPLATE', 'data_dir', conf_dir)
    modify_ini(issuer_conf_dir, 'ISSUERINFO', 'usb_name', conf_dir)
    modify_ini(issuer_conf_dir, 'ISSUERINFO', 'unsigned_certificates_dir', unsigned_cert_dir)
    modify_ini(issuer_conf_dir, 'ISSUERINFO', 'work_dir', work_dir)
    
def write_roster(list_NAME, list_DOCID, list_PDFinfo, export_file):
    headers = ['name', 'pubkey', 'identity', 'PDFinfo']
    csvfile = open(export_file, 'w')
    writer = csv.DictWriter(csvfile, headers)
    writer.writeheader()
    for i in range(0, len(list_NAME)):
        writer.writerow({'name' : list_NAME[i],
                         'pubkey': 'ecdsa-koblitz-pubkey:' + str(hashlib.sha256(b'dummy').hexdigest()),
                         'identity' : list_DOCID[i], 
                         'PDFinfo' : list_PDFinfo[i]})

def create_roster(import_path, name_pattern):
    re_DOCID = '(?P<DOCID>[0-9a-zA-Z]+)'
    re_NAME = '(?P<NAME>[a-zA-Z ]+)'
    regex = name_pattern.replace('|DOCID|', re_DOCID).replace('|NAME|', re_NAME)

    list_NAME = []
    list_DOCID = []
    list_PDFinfo = []
    count = 0

    for filename in glob.glob(os.path.join(import_path, '*.pdf')):
        pr = filename.split('/')[-1] if '/' in filename else filename
        if '.pdf' in pr:
            pr = pr.replace('.pdf', '')
        res = re.match(regex, pr)
        if res:
            list_NAME.append(res.group('NAME'))
            list_DOCID.append(res.group('DOCID'))
            list_PDFinfo.append(getBase64(filename))
            count = count + 1

    write_roster(list_NAME, list_DOCID, list_PDFinfo, roster_dir)

    return [list_DOCID, count]

def create_template():
    conf = tpl.get_config(tools_conf_dir)
    tpl.create_certificate_template(conf)

def create_certificates():
    conf = ist.get_config(tools_conf_dir)
    ist.create_unsigned_certificates_from_roster(conf)

def issue_certificates(export_path):
    modify_ini(issuer_conf_dir, 'ISSUERINFO', 'blockchain_certificates_dir', export_path)
    try:
        parsed_config = config.get_config(issuer_conf_dir)
        tx_id = isu.main(parsed_config)
        if tx_id:
            logging.info('Transaction id is %s', tx_id)
        else:
            logging.error('Certificate issuing failed')
            exit(1)

    except Exception as ex:
        logging.error(ex, exc_info=True)
        exit(1)

# only_generate_this_batch : whether the summary contains certificates which are not issued this time

def generate_summary(cert_path, export_path, list_DOCID, only_generate_this_batch = True):
    output = dict()
    for filename in glob.glob(os.path.join(cert_path, '*.json')):
        with open(filename, 'rb') as f:
            data = json.load(f)
            identity = data['recipient']['identity']
            id = data['id']
            issuedtime = data['issuedOn']
            if identity in list_DOCID or not only_generate_this_batch:
                usr = dict()
                usr['cert_id'] = id
                usr['issued_time'] = issuedtime
                output[identity] = usr
    with open(export_path, 'w') as f:
        json.dump(output, f, indent = 4)
    print('Summary has been written to ' + export_path)