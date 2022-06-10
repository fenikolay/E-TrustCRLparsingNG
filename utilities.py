import os
import sys
import base64
import shutil
import OpenSSL
import datetime
from urllib import request
from lxml import etree
from model import CERT, UC, WatchingCRL, WatchingCustomCRL, WatchingDeletedCRL
from configurator import configurator

def progressbar(cur, total=100):
    percent = '{:.2%}'.format(cur / total)
    sys.stdout.write('\r')
    # sys.stdout.write("[%-50s] %s" % ('=' * int(math.floor(cur * 50 / total)),percent))
    sys.stdout.write("[%-100s] %s\n" % ('=' * int(cur), percent))
    sys.stdout.flush()

def schedule(block_num, block_size, total_size):
    if total_size == 0:
        percent = 0
    else:
        percent = block_num * block_size / total_size
    if percent > 1.0:
        percent = 1.0
    percent = percent * 100
    print("\n download : %.2f%%" % percent)
    progressbar(percent)


def get_info_xlm(type_data, xml_file='tsl.xml'):
    current_version = 'unknown'
    last_update = 'unknown'
    with open(xml_file, "rt", encoding="utf-8") as obj:
        xml = obj.read().encode()

    root = etree.fromstring(xml)
    for row in root.getchildren():
        if row.text:
            if row.tag == 'Версия':
                current_version = row.text
        if row.text:
            if row.tag == 'Дата':
                last_update = row.text
    if type_data == 'current_version':
        return current_version
    if type_data == 'last_update':
        return last_update

def open_file(file_name, file_type, url='None'):
    type_crypto_dll = ''
    folder = ''
    if file_type == 'cer':  # CryptExtOpenCER «файл» Открывает сертификат безопасности.
        type_crypto_dll = 'CryptExtOpenCER'
        folder = 'certs'
    elif file_type == 'crl':  # CryptExtOpenCRL «файл» Открывает список отзыва сертификатов.
        type_crypto_dll = 'CryptExtOpenCRL'
        folder = 'crls'
    elif file_type == 'cat':  # CryptExtOpenCAT «файл» Открывает каталог безопасности.
        type_crypto_dll = 'CryptExtOpenCAT'
        folder = 'cats'
    elif file_type == 'ctl':  # CryptExtOpenCTL «файл» Открывает список доверия сертификатов.
        type_crypto_dll = 'CryptExtOpenCTL'
        folder = 'ctls'
    elif file_type == 'p10':  # CryptExtOpenP10 «файл» Открывает запрос на сертификат.
        type_crypto_dll = 'CryptExtOpenP10'
        folder = 'p10s'
    elif file_type == 'p7r':  # CryptExtOpenP7R «файл» Открывает файл ответа на запрос сертификата.
        type_crypto_dll = 'CryptExtOpenP7R'
        folder = 'p7rs'
    elif file_type == 'pkcs7':  # CryptExtOpenPKCS7 «файл» Открывает сертификат PCKS #7.
        type_crypto_dll = 'CryptExtOpenPKCS7'
        folder = 'pkcs7s'
    elif file_type == 'str':  # CryptExtOpenSTR «файл» Открывает хранилище сериализированных сертификатов.
        type_crypto_dll = 'CryptExtOpenSTR'
        folder = 'strs'

    run_dll = "%SystemRoot%\\System32\\rundll32.exe cryptext.dll," + type_crypto_dll
    path = os.path.realpath(configurator.config['Folders'][folder] + "/" + file_name + "." + file_type)
    print(path)
    if not os.path.exists(path):
        if file_type == 'cer':
            save_cert(file_name, configurator.config['Folders']['certs'])
        elif file_type == 'crl':
            download_file(url, file_name + '.crl', configurator.config['Folders']['crls'])
    else:
        open_crl = run_dll + "  " + path
        os.system(open_crl)

def save_cert(key_id, folder):
    for certs in CERT.select().where(CERT.KeyId == key_id):
        with open(folder + "/" + certs.KeyId + ".cer", "wb") as file:
            file.write(base64.decodebytes(certs.Data.encode()))
        if folder == configurator.config['Folders']['certs']:
            os.startfile(os.path.realpath(configurator.config['Folders']['certs']))
            print(os.path.realpath(configurator.config['Folders']['certs']))
        elif folder == configurator.config['Folders']['to_uc']:
            os.startfile(os.path.realpath(configurator.config['Folders']['to_uc']))
            print(os.path.realpath(configurator.config['Folders']['to_uc']))


def copy_crl_to_uc(rki):
    if os.path.exists(configurator.config['Folders']['crls'] + '/' + rki + '.crl'):
        shutil.copy2(configurator.config['Folders']['crls'] + '/' + rki + '.crl', configurator.config['Folders']['to_uc'] + '/' + rki + '.crl')
        configurator.logg.info('Found ' + configurator.config['Folders']['crls'] + '/' + rki + '.crl, copy.')
    else:
        configurator.logg.info('Not found ' + configurator.config['Folders']['crls'] + '/' + rki + '.crl')





def check_custom_crl(id_custom_crl, name, id_key, url_crl=''):
    issuer = {}
    if not os.path.isfile(configurator.config['Folders']['crls'] + '/' + str(id_key) + '.crl'):
        if not download_file(url_crl,
                             id_key + '.crl',
                             configurator.config['Folders']['crls'],
                             'custome',
                             str(id_custom_crl),
                             'Yes') == 'down_success':
            print('Warning: check_custom_crl::down_error ' + name)
            configurator.logg.warning('Check_custom_crl::down_error ' + name)
            return 'down_error'
    crl = OpenSSL.crypto.load_crl(OpenSSL.crypto.FILETYPE_ASN1,
                                  open('crls/' + str(id_key) + '.crl', 'rb').read())
    crl_crypto = crl.get_issuer()
    cryptography = crl.to_cryptography()

    for var, data in crl_crypto.get_components():
        issuer[var.decode("utf-8")] = data.decode("utf-8")

    query_uc = UC.select().where(UC.OGRN == issuer['OGRN'], UC.INN == issuer['INN'])
    for uc_data in query_uc:
        name = uc_data.Name
    query_update = WatchingCustomCRL.update(INN=issuer['INN'],
                                            OGRN=issuer['OGRN'],
                                            status='Info: Filetype good',
                                            last_update=cryptography.last_update + datetime.timedelta(hours=5),
                                            next_update=cryptography.next_update + datetime.timedelta(hours=5)). \
        where(WatchingCustomCRL.ID == id_custom_crl)
    query_update.execute()
    issuer['INN'] = 'Unknown'
    issuer['OGRN'] = 'Unknown'
    configurator.logg.info('Check_custom_crl()::success ' + name)
    return 'check_success'
    # query_update = WatchingCustomCRL.update(status='Warning: FILETYPE ERROR',
    #                                         last_update='1970-01-01',
    #                                         next_update='1970-01-01').where(
    #     WatchingCustomCRL.ID == id_custom_crl)


def check_crl(id_wc, name_wc, key_id_wc, url_crl=''):
    if not os.path.isfile(configurator.config['Folders']['crls'] + '/' + str(key_id_wc) + '.crl'):
        if download_file(url_crl,
                         key_id_wc + '.crl',
                         configurator.config['Folders']['crls'],
                         'current',
                         str(id_wc),
                         'Yes') == 'down_success':
            crl = OpenSSL.crypto.load_crl(
                OpenSSL.crypto.FILETYPE_ASN1,
                open(configurator.config['Folders']['crls'] + '/' + str(key_id_wc) + '.crl', 'rb').read())
            cryptography = crl.to_cryptography()
            query_update = WatchingCRL. \
                update(status='Info: Filetype good',
                       last_update=cryptography.last_update + datetime.timedelta(hours=5),
                       next_update=cryptography.next_update + datetime.timedelta(hours=5)).where(
                           WatchingCRL.ID == id_wc)
            query_update.execute()
            configurator.downlog.info('Check_crl()::success ' + name_wc)
            return 'check_success'
        else:
            configurator.downlog.warning('Check_crl()::down_error ' + name_wc)
            return 'down_error'
    else:
        crl = OpenSSL.crypto.load_crl(
            OpenSSL.crypto.FILETYPE_ASN1,
            open(configurator.config['Folders']['crls'] + '/' + str(key_id_wc) + '.crl', 'rb').read())
        cryptography = crl.to_cryptography()
        query_update = WatchingCRL. \
            update(status='Info: Filetype good',
                   last_update=cryptography.last_update + datetime.timedelta(hours=5),
                   next_update=cryptography.next_update + datetime.timedelta(hours=5)).where(
                       WatchingCRL.ID == id_wc)
        query_update.execute()
        configurator.downlog.info('Check_crl()::success ' + name_wc)
        return 'check_success'
    # query_update = WatchingCRL.update(status='Warning: FILETYPE ERROR',
    #                                   last_update='1970-01-01',
    #                                   next_update='1970-01-01').where(WatchingCRL.ID == id_wc)
    # query_update.execute()


def check_for_import_in_uc():
    folder = configurator.config['Folders']['crls']
    current_datetimes = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    current_datetime = datetime.datetime.strptime(current_datetimes, '%Y-%m-%d %H:%M:%S')
    minuts = int(configurator.config['Update']['timebeforeupdate'])
    days = int(configurator.config['Update']['deltaupdateinday'])
    print(current_datetime)
    current_datetime = current_datetime + datetime.timedelta(minutes=minuts)
    print(current_datetime)
    before_current_date = datetime.datetime.now() - datetime.timedelta(days=days)
    query_1 = WatchingCRL.select()
    query_2 = WatchingCustomCRL.select()
    count = 0
    return_list_msg = ''
    for wc in query_1:
        if current_datetime > wc.next_update > before_current_date:
            print('Info: Need to download current', wc.Name, current_datetime, wc.last_download, wc.last_update,
                  wc.next_update)
            if download_file(wc.UrlCRL, wc.KeyId + '.crl', folder, 'current', wc.ID, 'Yes') == 'down_success':

                shutil.copy2(configurator.config['Folders']['crls'] + '/' + wc.KeyId + '.crl',
                             configurator.config['Folders']['to_uc'] + '/' + 'current_' + wc.KeyId + '.crl')
                check_crl(wc.ID, wc.Name, wc.KeyId)
                return_list_msg = return_list_msg + ';' + wc.KeyId + ' : ' + wc.Name
                count = count + 1
    for wcc in query_2:
        if current_datetime > wcc.next_update > before_current_date:
            print('Info: Need to download custom', wcc.Name, current_datetime, wcc.last_download, wcc.last_update,
                  wcc.next_update)
            if download_file(wcc.UrlCRL, wcc.KeyId + '.crl', folder, 'custome', wcc.ID, 'Yes') == 'down_success':

                shutil.copy2(configurator.config['Folders']['crls'] + '/' + wcc.KeyId + '.crl',
                             configurator.config['Folders']['to_uc'] + '/' + 'custom_' + wcc.KeyId + '.crl')
                check_custom_crl(wcc.ID, wcc.Name, wcc.KeyId)
                return_list_msg = return_list_msg + ';' + wcc.KeyId + ' : ' + wcc.Name
                count = count + 1
    if count > 0:
        configurator.logg.info('Copied ' + str(count) + ' count\'s CRL')
        return return_list_msg
    else:
        configurator.logg.info('There are no updates for CRL')
        return 'NaN'


def download_file(file_url, file_name, folder, type_download='', w_id='', set_dd='No'):
    path = folder + '/' + file_name  # + '.' + type_file
    try:
        if configurator.config['Proxy']['proxyon'] == 'Yes':
            proxy = request.ProxyHandler(
                {'https': 'https://' + configurator.config['Proxy']['ip'] + ':' + configurator.config['Proxy']['port'],
                 'http': 'http://' + configurator.config['Proxy']['ip'] + ':' + configurator.config['Proxy']['port']})
            opener = request.build_opener(proxy)
            request.install_opener(opener)
            configurator.logg.info('Used proxy', 'info', '6')
        request.urlretrieve(file_url, path, schedule)
    except Exception:
        if set_dd == 'Yes':
            if type_download == 'current':
                query_update = WatchingCRL.update(download_status='Error: Download failed',
                                                  last_download=datetime.datetime.now()
                                                  .strftime('%Y-%m-%d %H:%M:%S')
                                                  ).where(WatchingCRL.ID == w_id)
                query_update.execute()
            elif type_download == 'custome':
                query_update = WatchingCustomCRL.update(download_status='Error: Download failed',
                                                        last_download=datetime.datetime.now()
                                                        .strftime('%Y-%m-%d %H:%M:%S')
                                                        ).where(WatchingCustomCRL.ID == w_id)
                query_update.execute()
        else:
            if type_download == 'current':
                query_update = WatchingCRL.update(download_status='Error: Download failed'
                                                  ).where(WatchingCRL.ID == w_id)
                query_update.execute()
            elif type_download == 'custome':
                query_update = WatchingCustomCRL.update(download_status='Error: Download failed'
                                                        ).where(WatchingCustomCRL.ID == w_id)
                query_update.execute()
        configurator.downlog.info('Download failed ' + file_url)
        return 'down_error'
    else:
        if set_dd == 'Yes':
            if type_download == 'current':
                query_update = WatchingCRL.update(download_status='Info: Download successfully',
                                                  last_download=datetime.datetime.now()
                                                  .strftime('%Y-%m-%d %H:%M:%S')
                                                  ).where(WatchingCRL.ID == w_id)
                query_update.execute()
            elif type_download == 'custome':
                query_update = WatchingCustomCRL.update(download_status='Info: Download successfully',
                                                        last_download=datetime.datetime.now()
                                                        .strftime('%Y-%m-%d %H:%M:%S')
                                                        ).where(WatchingCustomCRL.ID == w_id)
                query_update.execute()
        else:
            if type_download == 'current':
                query_update = WatchingCRL.update(download_status='Info: Download successfully'
                                                  ).where(WatchingCRL.ID == w_id)
                query_update.execute()
            elif type_download == 'custome':
                query_update = WatchingCustomCRL.update(download_status='Info: Download successfully'
                                                        ).where(WatchingCustomCRL.ID == w_id)
                query_update.execute()
        configurator.downlog.info('Download successfully ' + file_url)
        return 'down_success'


def export_all_watching_crl():
    query = WatchingCRL.select()
    query_2 = WatchingCustomCRL.select()
    with open(r"crl_list.txt", "w") as file:
        for url in query:
            file.write(url.UrlCRL + '\n')
    file.close()
    with open(r"crl_list.txt", "a") as file:
        for url in query_2:
            file.write(url.UrlCRL + '\n')
    file.close()


def exist_crl_in_custom_watch():
    query = WatchingCRL.select()
    for row in query:
        if WatchingCustomCRL.select().where(WatchingCustomCRL.KeyId == row.KeyId).count() > 0:
            print(row.KeyId, ' exist')

