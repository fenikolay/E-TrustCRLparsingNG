from msilib.schema import Error
import os, sys
import configparser
import datetime
import logging
from logging.config import fileConfig
from tkinter import E

DEFAULT_ETRUST_URL = 'https://e-trust.gosuslugi.ru/CA/DownloadTSL?schemaVersion=0'
DEFAULT_ETRUST_FILENAME = 'tsl.xml'
BASE_DIR = os.getcwd()
DEFAULT_CONFIG_FILENAME = 'settings.ini'
LOG_SUBDIR = 'logs'
MAIN_UC_OGRN = '1047702026701'
SELF_UC_OGRN = '1020203227263'
DEFAULT_MAIN_LOGNAME = 'etrust.log'
DEFAULT_DOWNLOAD_LOGNAME = 'etrust_download.log'
LOG_FORMAT = r'%(asctime)s - %(levelname)s - %(message)s'
DATE_FORMAT = r'%d-%m-%Y %H:%M:%S %z'
ROTATING_FILE_HANDLER_KWARGS = r'{"maxBytes": 1048576, "backupCount": 10, "encoding": "utf8"}'
FILE_HANDLER_KWARGS = r'{"encoding": "utf8"}'
MAIN_LOG_NAME = 'logg'
DOWNLOAD_LOG_NAME = 'downlog'


DEFAULT_CONFIGURATION = {
    'BaseDir': {
        'cwd': BASE_DIR
    },
    'ETrust' : {
        'url': DEFAULT_ETRUST_URL,
        'file': DEFAULT_ETRUST_FILENAME
    },
    'Folders': {
        'certs': 'certs',
        'crls': 'crls',
        'tmp': 'temp',
        'logs': LOG_SUBDIR,
        'to_uc': 'to_uc',
        'uc': 'uc'
    },
    'MainWindow': {
        'width': '1100',
        'height': '650',
        'saveWidth': 'No',
        'AllowResize': 'Yes'
    },
    'Bd': {
        'type': 'sqlite3',
        'name': 'cert_crl.db'
    },
    'Socket': {
        'timeout': 'No'
    },
    'Listing': {
        'uc': '500',
        'crl': '500',
        'cert': '500',
        'watch': '500'
    },
    # windowsvista, Windows, Fusion
    'Style': {
        'window': 'Fusion',
        'extendetColorInfo': 'No'
    },
    'Proxy': {
        'proxyOn': 'No',
        'ip': '',
        'port': '',
        'login': '',
        'password': ''
    },
    'Update': {
        'priority': 'custom',
        'advancedChecking': 'Yes',
        'viewingCRLlastNextUpdate': 'Yes',
        'allowupdatecrlbystart': 'No',
        'allowupdatetslbystart': 'No',
        'deltaupdateinday': '10',
        'timebeforeupdate': '20',
        'main_uc_ogrn': MAIN_UC_OGRN, # Продубливано в секции Custom
        'self_uc_ogrn': SELF_UC_OGRN  # Продубливано в секции Custom
    },
    'Backup': {
        'backUPbyStart': 'Yes'
    },
    'Tabs': {
        'ucLimit': '500',
        'ucAllowDelete': 'No',
        'crlLimit': '500',
        'crlAllowDelete': 'No',
        'certLimit': '500',
        'certAllowDelete': 'No',
        'wcLimit': '500',
        'wcAllowDelete': 'No',
        'wccLimit': '500',
        'wccAllowDelete': 'No',
        'wcdLimit': '500',
        'wcdAllowDelete': 'No'
    },
    'Schedule': {
        'allowSchedule': 'No',
        'weekUpdate': 'All',
        'timeUpdate': '1M',
        'periodUpdate': '9:00; 12:00; 16:00',
        'allowUpdateTSLbyStart': 'No',
        'allowUpdateCRLbyStart': 'No',
        'rangeUpdateCRL': '5day'
    },
    'Sec': {
        'allowImportCRL': 'No',
        'allowExportCRL': 'No',
        'allowDeleteWatchingCRL': 'No',
        'allowDownloadButtonCRL': 'Yes',
        'allowCheckButtonCRL': 'Yes'
    },
    'Logs': {
        'dividelogsbyday': 'Yes',
        'dividelogsbysize': '1024',
        'loglevel': '9'
    },
    'XMPP': {
        'server': '',
        'login': '',
        'password': '',
        'tosend': '',
        'sendinfoerr': 'No',
        'sendinfonewcrl': 'No',
        'sendinfonewtsl': 'No'
    },
    'loggers': {
        'keys': 'root, download',
    },
    'logger_root': {
        'level': 'NOTSET',
        'handlers': 'logrotate',
        'qualname': MAIN_LOG_NAME
        },
    'logger_download': {
        'level': 'INFO',
        'handlers': 'updfile',
        'propagate': '1',
        'qualname': DOWNLOAD_LOG_NAME
    },
    'handlers': {
        'keys': 'logrotate, updfile'
    },
    'formatters': {
        'keys': 'mainform'
    },
    'handler_logrotate': {
        'class': 'logging.handlers.RotatingFileHandler',
        'args': f'("{os.path.join(BASE_DIR, LOG_SUBDIR, DEFAULT_MAIN_LOGNAME)}", "a")',
        'kwargs': ROTATING_FILE_HANDLER_KWARGS,
        'formatter': 'mainform'
    },
    'handler_updfile': {
        'class': 'FileHandler',
        'args': f'("{os.path.join(BASE_DIR, LOG_SUBDIR, DEFAULT_DOWNLOAD_LOGNAME)}", "w")',
        'kwargs': FILE_HANDLER_KWARGS,
        'formatters': 'mainform'
    },
    'formatter_mainform':{
        'format': LOG_FORMAT,
        'datefmt': DATE_FORMAT,
    },
    'Custom': {
        'main_uc_ogrn': MAIN_UC_OGRN,
        'self_uc_ogrn': SELF_UC_OGRN
    }                            
}

class Configurator():
    """
    Объект загружающий, обновляющий и сохраняющий конфигурацию
    """
    def __init__(self):
        self.config = configparser.ConfigParser(
            comment_prefixes=('#',),
            interpolation=configparser.ExtendedInterpolation()
        )
        self.configure()

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Configurator, cls).__new__(cls)
        return cls.instance

    def set_default_config(self, section=None):
        if section is not None:
            self.config[section] = DEFAULT_CONFIGURATION[section]
        else:
            for section in DEFAULT_CONFIGURATION.keys():
                self.config[section] = DEFAULT_CONFIGURATION[section]
    
    def write_configuration(self, filename=DEFAULT_CONFIG_FILENAME):
        with open(filename, 'w') as configfile:
            self.config.write(configfile)
   
    def create_folders(self, folders):
        for folder in folders:
            if not os.path.exists(folder):
                try:
                    os.makedirs(folder)
                except Exception as e:
                    print(e)

    def read_update_config_file(self, filename=DEFAULT_CONFIG_FILENAME):
        if os.path.isfile(filename):
            self.config.read(filename)
            for section in DEFAULT_CONFIGURATION.keys():
                if section in self.config:
                    for key in DEFAULT_CONFIGURATION[section]:
                        if key not in self.config[section]:
                            self.config.set(section, key, DEFAULT_CONFIGURATION[section][key])
                else:
                    self.set_default_config(section)
        else:
            self.set_default_config()
        self.write_configuration(filename)

    def set_value_in_property_file(self, filename, section, key, value):
        self.config.set(section, key, value)
        self.write_configuration(filename)

    def configure(self):
        #with open(os.path.join(os.getcwd(), 'error.log'), 'w', encoding='utf8') as error:
        #    sys.stderr = error
        self.read_update_config_file()
        self.create_folders(self.config['Folders'].values())
        logging.config.fileConfig(self.config)
        self.logg = logging.getLogger()
        self.downlog = logging.getLogger('downlog')

configurator = Configurator()


