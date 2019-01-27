# This helper is intended to reduce the calling of BTC api to avoid reaching the limit

import time
import json
import fcntl
import logging
import requests
import datetime

from path_helpers import *

TESTNET_INTERVAL = 60 # in sec
MAINNET_INTERVAL = 30 # in sec

def get_bcypher_token():
    return 'cdeda4b5e2ae4c52b85fcd38327663ba'

def get_address(tx_id, TOKEN = None, chain = None):
    if TOKEN == None and chain == None:
        logging.error('Parameter missing.')
        return
    
    logging.info('Requesting for the address of ' + tx_id + ' ...')
    
    if chain == None:
        chain = read_ini(get_issuer_conf_dir(TOKEN), 'ISSUERINFO', 'chain')

    if 'testnet' in chain or 'Testnet' in chain:
        url = 'https://api.blockcypher.com/v1/btc/test3/txs/' + tx_id + '?token=' + get_bcypher_token()
        transaction_data = requests.get(url).json()
        if 'error' in transaction_data:
            logging.error(transaction_data['error'])
            return ''
        return transaction_data['inputs'][0]['addresses'][0]
    else:
        url = 'https://chain.api.btc.com/v3/tx/' + tx_id + '?verbose=2'
        transaction_data = requests.get(url).json()
        if transaction_data['err_no'] != 0:
            logging.error(transaction_data['err_msg'])
            return ''
        return transaction_data['data']['inputs'][0]['prev_addresses'][0]

def get_latest_transaction(pubkey, TOKEN = None, chain = None):
    if TOKEN == None and chain == None:
        logging.error('Parameter missing.')
        return

    logging.info('Requesting for the latest transaction of ' + pubkey + ' ...')
    
    if chain == None:
        chain = read_ini(get_issuer_conf_dir(TOKEN), 'ISSUERINFO', 'chain')
   
    if 'testnet' in chain or 'Testnet' in chain:
        url = 'https://api.blockcypher.com/v1/btc/test3/addrs/' + pubkey + "?token=" + get_bcypher_token()
        user_data = requests.get(url).json()
        if 'error' in user_data:
            logging.error(user_data['error'])
            return 'retry'
        return user_data['txrefs'][0]['tx_hash']
    else:
        url = 'https://chain.api.btc.com/v3/address/' + pubkey + '/tx'
        user_data = requests.get(url).json()
        if user_data['err_no'] != 0:
            logging.error(user_data['err_msg'])
            return 'retry'
        return user_data['data']['list'][0]['hash']

def get_confirmation(tx_id, TOKEN = None, chain = None):    
    if TOKEN == None and chain == None:
        logging.error('Parameter missing.')
        return

    logging.info('Requesting for the confirmation number of ' + tx_id + ' ...')
    
    if chain == None:
        chain = read_ini(get_issuer_conf_dir(TOKEN), 'ISSUERINFO', 'chain')
    
    cache_data = dict()

    try:
        cache_data = json.load(get_api_cache_dir())
        last_upd_time = cache_data[tx_id]['upd_time']
        if int(time.time()) - last_upd_time <= (TESTNET_INTERVAL if 'testnet' in chain else MAINNET_INTERVAL):
            return cache_data[tx_id]['confirmations']
    except:
        pass

    if 'testnet' in chain or 'Testnet' in chain:
        url = 'https://api.blockcypher.com/v1/btc/test3/txs/' + tx_id + '?token=' + get_bcypher_token()
        transaction_data = requests.get(url).json()
        if 'error' in transaction_data:
            logging.error(transaction_data['error'])
            return 0
        ret = transaction_data['confirmations']
    else:
        url = 'https://chain.api.btc.com/v3/tx/' + tx_id + '?verbose=1'
        transaction_data = requests.get(url).json()
        if transaction_data['err_no'] != 0:
            logging.error(transaction_data['err_msg'])
            return 0
        ret = transaction_data['data']['confirmations']

    cache_data[tx_id] = dict()
    cache_data[tx_id]['upd_time'] = int(time.time())
    cache_data[tx_id]['confirmations'] = ret
    with open(get_api_cache_dir(), 'w') as file:
        json.dump(cache_data, file)

    return ret

def get_recommended_tx_fee():
    logging.info('Requesting for the recommended transaction fee ...')
    data = requests.get('https://bitcoinfees.earn.com/api/v1/fees/recommended').json()
    return data['fastestFee']