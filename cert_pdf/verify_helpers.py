import json
import requests

from cert_verifier import verifier
from btc_api_helpers import *

# FUNCTION check_confirmation_and_issuer - Check whether the transaction is confirmed 
#                                          and whether the cert is issued by issuer in pubkey_list

def get_txid(cert_path):

    with open(cert_path) as f:
        data = json.load(f)
        tx_id = data['signature']['anchors'][0]['sourceId']
    
    return tx_id

def check_confirmation_and_issuer(cert_path, pubkey_list):
    
    ret = dict()
    
    with open(cert_path) as f:
        data = json.load(f)
        chain = data['signature']['anchors'][0]['chain']
        tx_id = data['signature']['anchors'][0]['sourceId']
        
        try:
            ret['transaction is confirmed'] = get_confirmation(tx_id, chain = chain) > 0
        except Exception as e:
            print(e)
            return

        ret['issued by specific issuer'] = get_address(tx_id, chain = chain) in pubkey_list

    return ret

def cert_verify(cert_path):
    return verifier.verify_certificate_file(cert_path)