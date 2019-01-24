import os
import sys
import json
import uuid
import fcntl
import base64
import signal
import datetime

import issuer_helpers
import verify_helpers
import path_helpers

# Test public key

pubkey_list = ['mubib9QNSNfBZkphQb3cCXG6giGKzA9k3X']

def generate_token():
    return str(uuid.uuid4())
    
def add_log(title, str):
    file = open(path_helpers.get_api_log_dir(), 'a')
    fcntl.flock(file.fileno(), fcntl.LOCK_EX)
    print('[%s] [%s] %s' % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), title, str), file = file)
    file.close()

def insert_job_log(str, inc = False, replace = False):
    if replace:
        JOB_LOG['state'] = str
    if inc:
        JOB_LOG['current_task'] += 1
    file_json = open(path_helpers.get_stage_json_dir(TOKEN), 'w')
    json.dump(JOB_LOG, file_json, indent = 4)

    file_json.close()
    file_log = open(path_helpers.get_stage_log_dir(TOKEN), 'a')
    print('[%s] %s' % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), str), file = file_log)
    file_log.close()

def go_task(f, msg_str, print_suc = True):
    try:
        print('\n[INFO] %s ...' % msg_str)
        insert_job_log('%s ...' % msg_str, inc = True, replace = True)
        f()
    except Exception as e:
        print('\n[INFO] Failed. Error message: %s.' % str(e))
        add_log('ERROR', 'The job <%s> failed. Please see log file <%s> for details.' % (TOKEN, path_helpers.get_stage_log_dir(TOKEN)))
        insert_job_log('Failed. Error message: %s.' % str(e))
        insert_job_log('Job failed.', replace = True)
        insert_job_log('Cleaning all cache files ...')
        issuer_helpers.clear()
        exit(1)
    else:
        if print_suc:
            insert_job_log('Succeed.')

def tmp_create_roster(import_path, name_pattern):
    global file_count
    file_count = issuer_helpers.create_roster(import_path, name_pattern)

def tmp_issue_certificates(pubkey):
    global issue_ret
    issue_ret = issuer_helpers.issue_certificates(pubkey)
    if not issue_ret[1]:
        print('\n[INFO] Failed. Please see log file <%s> for details.' % path_helpers.get_stage_log_dir(TOKEN))
        add_log('ERROR', 'The job <%s> failed. Please see log file <%s> for details.' % (TOKEN, path_helpers.get_stage_log_dir(TOKEN)))
        insert_job_log('Job failed.', replace = True)
        insert_job_log('Cleaning all cache files ...')
        issuer_helpers.clear()
        exit(1)

# FUNCTION issue_batch - Load a set of PDF files and finally deploy them on the blockchain
#
# import_path - the directory where all PDFs are stored which need to be issued
# export_path - the destination of the issued certs (json files)
# itsc - the itsc account of the user who raises this issuing
# name_pattern - the format of filename. |NAME|, |DOCID| are wildcards to match the corresponding info
#               PLAESE DON'T include '.pdf' in namePattern

def issue_batch(import_path, export_path, pubkey, psw_file, itsc = None, name_pattern = '|DOCID|-|NAME|'):

    global TOKEN
    global JOB_LOG
    global file_count
    global issue_ret

    TOKEN = generate_token()
    JOB_LOG = dict()
    file_count = 0
    issue_ret = ['', '']

    os.makedirs(os.path.split(path_helpers.get_api_log_dir())[0], exist_ok = True)
    os.makedirs(os.path.split(path_helpers.get_stage_log_dir(TOKEN))[0], exist_ok = True)

    JOB_LOG['id'] = TOKEN
    JOB_LOG['current_task'] = 0
    JOB_LOG['total_tasks'] = 10
    JOB_LOG['state'] = ''

    
    add_log('START', 'A new job is initiated by user <%s> with the job ID <%s>.\nThe state of this job can be found in file <%s>.' % (itsc, TOKEN, path_helpers.get_stage_log_dir(TOKEN)))
    insert_job_log('The job <%s> is started by user <%s>.' % (TOKEN, itsc), replace = True)
    print('\n[INFO] The job ID of this calling is ' + TOKEN)

    go_task(lambda: issuer_helpers.start(TOKEN, export_path), 'Creating staging folder')
    go_task(lambda: issuer_helpers.modify_conf(pubkey, psw_file), 'Modifying configuration files')
    go_task(lambda: tmp_create_roster(import_path, name_pattern), 'Creating roster file')
    
    if file_count == 0:
        print('\n[INFO] There is no valid PDF file found, the process will terminate.\n')
        add_log('ERROR', 'The job <%s> failed. Because there is no valid PDF file found.' % TOKEN)
        insert_job_log('There is no valid PDF file found, the process will terminate.')
        insert_job_log('Job failed.', replace = True)
        insert_job_log('Cleaning all cache files ...')
        issuer_helpers.clear()
        exit(1)

    go_task(lambda: issuer_helpers.create_template(), 'Creating certificate templates')
    go_task(lambda: issuer_helpers.create_certificates(), 'Instantiating certificates')
    go_task(lambda: tmp_issue_certificates(pubkey), 'Issuing certificates')
    go_task(lambda: issuer_helpers.generate_summary(export_path), 'Generating summary file and moving issued certs into the destination folder')
    go_task(lambda: issuer_helpers.wait(issue_ret[0]), 'Waiting the transaction to be confirmed')
    go_task(lambda: issuer_helpers.clear(), 'Cleaning working directory')
    
    insert_job_log('Job accomplished.', inc = True, replace = True)
    print('\n[INFO] All steps finished.\n')
    add_log('SUCCESS', 'The job <%s> succeed. Please go to <%s> to find the export files.' % (TOKEN, export_path))     

# FUNCTION verify_cert - Verify whether a cert
#                        1) is generated by specified issuer
#                        2) is confirmed on the blochchain / revoked / tampered
#
# pubkey_list - list of valid public keys of the issuer
# NOTE: only testnet and mainnet of bitcoin are supported

def verify_cert(cert_path, pubkey_list):
    
    result = []

    ret = verify_helpers.check_confirmation_and_issuer(cert_path, pubkey_list)
    ret2 = verify_helpers.cert_verify(cert_path)
    ret.update(ret2)

    prev = True
    for x in ret.keys():
        result.append({'name' : x, 'passed' : prev and ret[x]})
        if prev and ret[x]:
            msg = 'passed'
        elif prev and not ret[x]:
            msg = 'not passed'
        else:
            msg = 'skipped'
        print('%27s' % x + ' - ' + msg)
        prev = prev and ret[x]

    result.append({'name' : '*OVERALL VALIDATION', 'passed' : not False in ret.values()})
    print('%27s' % '*OVERALL VALIDATION' + ' - ' + ('PASSED' if not False in ret.values() else 'NOT PASSED'))

    return result

# FUNCTION extract_pdf - Extract the PDF file inside the cert json file

def extract_pdf(cert_path, export_path):
    try:
        with open(cert_path) as f:
            output = open(export_path, 'wb')
            data = json.load(f)
            output.write(base64.decodestring(data['PDFinfo'].encode('utf-8')))
            print('[INFO] Extract succeeded!')
    except Exception as e:
        print(e)

def clear_cache():
    add_log('INFO', 'A cache cleaning job is raised.')     
    issuer_helpers.clear(True)
    add_log('INFO', 'Cleaning finished.')     

def signal_handler(signal, frame):
    insert_job_log('The thread is interrupted.')
    insert_job_log('Job failed.', replace = True)
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

if __name__ == '__main__':
    issue_batch('./PDFs', './output', pubkey_list[0], './configuration/psw_testnet.txt')