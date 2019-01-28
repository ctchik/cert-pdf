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
        try:
            transaction_data = requests.get(url)
            td_json = transaction_data.json()
            if 'error' in td_json:
                logging.error(td_json['error'])
                return ''
            return td_json['inputs'][0]['addresses'][0]
        except Exception as e:
            logging.error('URL request result: ' + str(transaction_data.content))
            logging.error(str(e))
            logging.info('Will retry later ...')
            return 0
    else:
        url = 'https://chain.api.btc.com/v3/tx/' + tx_id + '?verbose=2'
        try:
            transaction_data = requests.get(url)
            td_json = transaction_data.json()
            if td_json['err_no'] != 0:
                logging.error(td_json['err_msg'])
                return ''
            return td_json['data']['inputs'][0]['prev_addresses'][0]
        except Exception as e:
            logging.error('URL request result: ' + str(transaction_data.content))
            logging.error(str(e))
            logging.info('Will retry later ...')
            return 0

def get_latest_transaction(pubkey, TOKEN = None, chain = None):
    if TOKEN == None and chain == None:
        logging.error('Parameter missing.')
        return

    logging.info('Requesting for the latest transaction of ' + pubkey + ' ...')
    
    if chain == None:
        chain = read_ini(get_issuer_conf_dir(TOKEN), 'ISSUERINFO', 'chain')
   
    if 'testnet' in chain or 'Testnet' in chain:
        url = 'https://api.blockcypher.com/v1/btc/test3/addrs/' + pubkey + "?token=" + get_bcypher_token()
        try:
            user_data = requests.get(url)
            ud_json = user_data.json()
            if 'error' in ud_json:
                logging.error(ud_json['error'])
                return 'retry'
            return ud_json['txrefs'][0]['tx_hash']
        except Exception as e:
            logging.error('URL request result: ' + str(user_data.content))
            logging.error(str(e))
            logging.info('Will retry later ...')
            return 'retry'
    else:
        url = 'https://chain.api.btc.com/v3/address/' + pubkey + '/tx'
        try:
            user_data = requests.get(url)
            ud_json = user_data.json()
            if ud_json['err_no'] != 0:
                logging.error(ud_json['err_msg'])
                return 'retry'
            return ud_json['data']['list'][0]['hash']
        except Exception as e:
            logging.error('URL request result: ' + str(user_data.content))
            logging.error(str(e))
            logging.info('Will retry later ...')
            return 'retry'

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
        try:
            transaction_data = requests.get(url)
            td_json = transaction_data.json()
            if 'error' in td_json:
                logging.error(td_json['error'])
                return 0
            ret = td_json['confirmations']
        except Exception as e:
            logging.error('URL request result: ' + str(transaction_data.content))
            logging.error(str(e))
            logging.info('Will retry later ...')
            return 0
    else:
        url = 'https://chain.api.btc.com/v3/tx/' + tx_id + '?verbose=1'
        try:
            transaction_data = requests.get(url)
            td_json = transaction_data.json()
            if td_json['err_no'] != 0:
                logging.error(td_json['err_msg'])
                return 0
            ret = td_json['data']['confirmations']
        except Exception as e:
            logging.error('URL request result: ' + str(transaction_data.content))
            logging.error(str(e))
            logging.info('Will retry later ...')
            return 0

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

def request_sleep(TOKEN = None, chain = None):
    if TOKEN == None and chain == None:
        logging.error('Parameter missing.')
        return
    
    if not chain:
        chain = read_ini(get_issuer_conf_dir(TOKEN), 'ISSUERINFO', 'chain')
    
    if 'testnet' in chain or 'Testnet' in chain:
        time.sleep(60)
    else:
        time.sleep(60)