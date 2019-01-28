import os
import pathlib
import configparser

def read_ini(ini_file, section, key):
    config = configparser.RawConfigParser(allow_no_value = True)
    config.read(ini_file)
    return config[section][key]

def modify_ini(ini_file, section, key, new_value):
    config = configparser.RawConfigParser(allow_no_value = True)
    config.optionxform = str
    config.read(ini_file)
    config.set(section, key, new_value)
    with open(ini_file, "w") as output:
        config.write(output)

OS_ROOT = str(pathlib.Path.home())
INI_FILE = os.path.join(OS_ROOT, '.cert_pdf')
ROOT_DIR = read_ini(INI_FILE, 'DIR', 'root_dir')
STAGE_DIR = os.path.join(ROOT_DIR, read_ini(INI_FILE, 'DIR', 'stage_dir'))

def get_latest_transaction_file_dir():
    return os.path.join(ROOT_DIR, read_ini(INI_FILE, 'DIR', 'latest_transaction'))

def get_issuer_conf_template_dir():
    return os.path.join(ROOT_DIR, read_ini(INI_FILE, 'TEMPLATE', 'issuer_conf'))

def get_tools_conf_template_dir():
    return os.path.join(ROOT_DIR, read_ini(INI_FILE, 'TEMPLATE', 'tools_conf'))

def get_image_template_dir():
    return os.path.join(ROOT_DIR, read_ini(INI_FILE, 'TEMPLATE', 'images_dir'))

def get_image_dir(token):
    return os.path.join(STAGE_DIR, token, 'images')

def get_summary_dir():
    return os.path.join(ROOT_DIR, read_ini(INI_FILE, 'DIR', 'summary_file'))

def get_summary_file_dir(token):
    return os.path.join(ROOT_DIR, read_ini(INI_FILE, 'DIR', 'summary_file'), token + '.json')

def get_conf_dir(token):
    return os.path.join(STAGE_DIR, token)

def get_work_dir(token):
    return os.path.join(STAGE_DIR, token, 'work')

def get_unsigned_cert_dir(token):
    return os.path.join(STAGE_DIR, token, 'unsigned_certificates')

def get_signed_cert_dir(token):
    return os.path.join(STAGE_DIR, token, 'signed_certificates')

def get_template_dir(token):
    return os.path.join(STAGE_DIR, token, 'templates')

def get_roster_dir(token):
    return os.path.join(STAGE_DIR, token, 'roster')

def get_roster_file_dir(token):
    return os.path.join(get_roster_dir(token), 'roster.csv')

def get_issuer_conf_dir(token):
    return os.path.join(get_conf_dir(token), 'issuer_conf.ini')

def get_tools_conf_dir(token):
    return os.path.join(get_conf_dir(token), 'tools_conf.ini')

def get_unissued_task_file_dir():
    return os.path.join(ROOT_DIR, read_ini(INI_FILE, 'DIR', 'unissued_task_file'))

def get_issued_task_file_dir():
    return os.path.join(ROOT_DIR, read_ini(INI_FILE, 'DIR', 'issued_task_file'))

def get_api_log_dir():
    return os.path.join(ROOT_DIR, read_ini(INI_FILE, 'DIR', 'api_log'))

def get_stage_json_dir(token):
    return os.path.join(ROOT_DIR, read_ini(INI_FILE, 'DIR', 'stage_log'), token, token + '.json')

def get_stage_log_dir(token):
    return os.path.join(ROOT_DIR, read_ini(INI_FILE, 'DIR', 'stage_log'), token, token + '.log')