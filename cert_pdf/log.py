import json
import fcntl
import datetime

import path_helpers

from vars import *

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