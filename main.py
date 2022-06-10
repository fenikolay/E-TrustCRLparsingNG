from PyQt5.QtGui import QTextCursor, QIcon, QPixmap, QColor, QBrush
from PyQt5.QtWidgets import QPushButton, QWidget, QTableWidgetItem, QHeaderView, QFileDialog, QMainWindow, QApplication
from PyQt5.QtCore import pyqtSignal, QThread, QObject
from PyQt5.Qt import Qt
from urllib import request
from lxml import etree
from ui_sub_main import Ui_Form
from ui_sub_main_crl import Ui_Form_crl
from ui_sub_main_add import Ui_Form_add
from ui_main import Ui_MainWindow

import base64
import datetime
import math
import os
import re
import shutil
import sys
import time
from contextlib import redirect_stdout, redirect_stderr

from model import UC, CERT, CRL, WatchingCRL, WatchingCustomCRL, WatchingDeletedCRL, Settings
from base64_codes import *
from configurator import configurator
from utilities import save_cert, download_file,  copy_crl_to_uc, export_all_watching_crl
from utilities import get_info_xlm, check_crl, check_custom_crl, check_for_import_in_uc


if not UC.table_exists():
    UC.create_table()
if not CERT.table_exists():
    CERT.create_table()
if not CRL.table_exists():
    CRL.create_table()
if not Settings.table_exists():
    Settings.create_table()
    Settings(name='ver', value=0).save()
    Settings(name='data_update', value='1970-01-01 00:00:00').save()
if not WatchingCRL.table_exists():
    WatchingCRL.create_table()
if not WatchingCustomCRL.table_exists():
    WatchingCustomCRL.create_table()
if not WatchingDeletedCRL.table_exists():
    WatchingDeletedCRL.create_table()


class DownloadAllCRL(QObject):

    threadInfoMessage = pyqtSignal(str)

    def __init__(self):

        super(DownloadAllCRL, self).__init__()
        self._step = 0
        self._isRunning = True

    def task(self):

        print('Info: Starting checking CRL')
        configurator.logg.info('Starting checking CRL')
        # self.threadInfoMessage.emit('Info: Starting checking CRL')
        if not self._isRunning:
            self._isRunning = True
            self._step = 0
        while self._isRunning:
            self._step += 1
            query_1 = WatchingCRL.select()
            query_2 = WatchingCustomCRL.select()
            counter_watching_crl_all = WatchingCRL.select().count()
            watching_custom_crl_all = WatchingCustomCRL.select().count()
            counter_watching_crl = 0
            counter_watching_custom_crl = 0
            self.threadInfoMessage.emit('Загрузка началась')
            for wc in query_1:
                counter_watching_crl = counter_watching_crl + 1
                file_url = wc.UrlCRL
                file_name = wc.KeyId + '.crl'
                # file_name = wc.UrlCRL.split('/')[-1]
                # file_name = wcc.KeyId
                folder = configurator.config['Folders']['crls']
                self.threadInfoMessage.emit(
                    str(counter_watching_crl) + ' из ' + str(
                        counter_watching_crl_all) + ' Загружаем: ' + str(
                        wc.Name) + ' ' + str(wc.KeyId))
                download_file(file_url, file_name, folder, 'current', wc.ID)
                # Downloader(str(wc.UrlCRL), str(wc.SerialNumber)+'.crl')
            print('WatchingCRL downloaded ' + str(counter_watching_crl))
            configurator.logg.info('WatchingCRL downloaded ' + str(counter_watching_crl))
            for wcc in query_2:
                counter_watching_custom_crl = counter_watching_custom_crl + 1
                file_url = wcc.UrlCRL
                file_name = wcc.KeyId + '.crl'
                # file_name = wcc.UrlCRL.split('/')[-1]
                # file_name = wcc.KeyId
                folder = configurator.config['Folders']['crls']
                self.threadInfoMessage.emit(
                    str(counter_watching_custom_crl) + ' из ' + str(
                        watching_custom_crl_all) + ' Загружаем: ' + str(
                        wcc.Name) + ' ' + str(wcc.KeyId))
                download_file(file_url, file_name, folder, 'custome', wcc.ID)
                # Downloader(str(wcc.UrlCRL), str(wcc.SerialNumber)+'.crl'
            self.threadInfoMessage.emit('Загрузка закончена')
            print('WatchingCustomCRL downloaded ' + str(counter_watching_custom_crl))
            configurator.downlog.info('WatchingCustomCRL downloaded ' + str(counter_watching_custom_crl))
            print('All download done, w=' + str(counter_watching_crl) + ', c=' + str(
                counter_watching_custom_crl))
            configurator.downlog.info('All download done, w=' + str(counter_watching_crl) + ', c=' + str(
                counter_watching_custom_crl))
            # self.ui.pushButton_4.setEnabled(True)
            self.stop()
        else:
            self._isRunning = False
        time.sleep(1)
        print('Info: Checking completed')
        configurator.logg.info('Checking completed')

    def stop(self):
        self._isRunning = False


class CheckCRL(QObject):
    threadInfoMessage = pyqtSignal(str)

    def __init__(self):
        super(CheckCRL, self).__init__()
        self._step = 0
        self._isRunning = True

    def task(self):

        print('Info: Starting checking CRL')
        configurator.logg.info('Starting checking CRL')
        self.threadInfoMessage.emit('Начинаем проверку')
        if not self._isRunning:
            self._isRunning = True
            self._step = 0
        while self._isRunning:
            self._step += 1

            folder = configurator.config['Folders']['crls']
            current_datetimes = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            current_datetime = datetime.datetime.strptime(current_datetimes, '%Y-%m-%d %H:%M:%S')
            before_current_date = datetime.datetime.now() - datetime.timedelta(days=5)
            query_1 = WatchingCRL.select()
            query_2 = WatchingCustomCRL.select()
            count = 0
            return_list_msg = ''
            for wc in query_1:
                if current_datetime > wc.next_update > before_current_date:
                    self.threadInfoMessage.emit('Скачиваем: ' + wc.Name)
                    if download_file(wc.UrlCRL, wc.KeyId + '.crl', folder, 'current', wc.ID,
                                     'Yes') == 'down_success':
                        shutil.copy2(configurator.config['Folders']['crls'] + '/' + wc.KeyId + '.crl',
                                     configurator.config['Folders']['to_uc'] + '/' + 'current_' + wc.KeyId + '.crl')
                        check_crl(wc.ID, wc.Name, wc.KeyId)
                        return_list_msg = return_list_msg + ';' + wc.KeyId + ' ' + wc.Name
                        count = count + 1
            for wcc in query_2:
                if current_datetime > wcc.next_update > before_current_date:
                    self.threadInfoMessage.emit('Скачиваем: ' + wcc.Name)
                    if download_file(wcc.UrlCRL, wcc.KeyId + '.crl', folder, 'custome', wcc.ID,
                                     'Yes') == 'down_success':
                        shutil.copy2(configurator.config['Folders']['crls'] + '/' + wcc.KeyId + '.crl',
                                     configurator.config['Folders']['to_uc'] + '/' + 'custom_' + wcc.KeyId + '.crl')
                        check_custom_crl(wcc.ID, wcc.Name, wcc.KeyId)
                        return_list_msg = return_list_msg + ';' + wcc.KeyId + ' ' + wcc.Name
                        count = count + 1
            if count > 0:
                print('Info: Copied ' + str(count) + ' count\'s CRL')
                configurator.downlog.info('Copied ' + str(count) + ' count\'s CRL')
            else:
                print('Info: There are no updates for CRL')
                configurator.downlog.info('Info: There are no updates for CRL')
            self.stop()
        else:
            self._isRunning = False
        time.sleep(1)
        print('Info: Checking completed')
        configurator.downlog.info('Info: Checking completed')
        self.threadInfoMessage.emit('Проверка завершена')

    def stop(self):
        self._isRunning = False


class MainWorker(QObject):

    threadMessageSender = pyqtSignal(str)
    threadTimerSender = pyqtSignal(str)
    threadButtonStartE = pyqtSignal(str)
    threadButtonStopE = pyqtSignal(str)
    threadButtonStartD = pyqtSignal(str)
    threadButtonStopD = pyqtSignal(str)
    threadInfoMessage = pyqtSignal(str)
    threadBefore = pyqtSignal(str)
    threadAfter = pyqtSignal(str)

    def __init__(self):
        super(MainWorker, self).__init__()
        self._step = 0
        self._seconds = 0
        self._minutes = 0
        self._hour = 0
        self._day = 0
        self._isRunning = True

    def task(self):

        timer_getting = configurator.config['Schedule']['timeUpdate']
        r = re.compile(r"([0-9]+)([a-zA-Z]+)")
        m = r.match(timer_getting)

        if m.group(2) == 'S':
            sec_to_get = int(m.group(1))
        elif m.group(2) == 'M':
            sec_to_get = int(m.group(1)) * 60
        elif m.group(2) == 'H':
            sec_to_get = int(m.group(1)) * 60 * 60
        elif m.group(2) == 'D':
            sec_to_get = int(m.group(1)) * 60 * 60 * 24
        else:
            print('error')
            sec_to_get = 0

        day_get = math.floor(sec_to_get / 60 / 60 / 24)
        hour_get = math.floor(sec_to_get / 60 / 60)
        minutes_get = math.floor(sec_to_get / 60)
        sec_get = math.floor(sec_to_get)

        day_start = 0
        hour_start = 0
        minutes_start = 0
        sec_start = 0
        if day_get > 0:
            day_start = day_get
        else:
            if hour_get > 0:
                hour_start = hour_get
            else:
                if minutes_get > 0:
                    minutes_start = minutes_get
                else:
                    if sec_get > 0:
                        sec_start = sec_get
                    else:
                        print('error')

        print('Info: Start monitoring CRL')
        configurator.downlog.info('Start monitoring CRL')
        self.threadInfoMessage.emit('Info: Start monitoring CRL')
        self.threadButtonStartD.emit('True')
        self.threadButtonStopE.emit('True')
        timer_b = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        timer_a = datetime.datetime.now() + datetime.timedelta(seconds=sec_to_get)
        timer_a = datetime.datetime.strftime(timer_a, '%Y-%m-%d %H:%M:%S')
        self.threadBefore.emit(timer_b)
        self.threadAfter.emit(timer_a)
        if not self._isRunning:
            self._isRunning = True
            self._step = 0
            self._seconds = 0
            self._minutes = 0
            self._hour = 0
            self._day = 0
        while self._isRunning:
            self._step += 1
            self._seconds += 1

            # ---------------------------------------------------
            if day_start == 0:
                hour_start -= 1
            if hour_start == 0:
                hour_start = 60
                day_start -= 1
            if minutes_start == 0:
                minutes_start = 60
                hour_start -= 1
            if sec_start == 0:
                sec_start = 60
                minutes_start -= 1
            # ---------------------------------------------------
            if self._seconds == 60:
                self._minutes += 1
                self._seconds = 0
            if self._minutes == 60:
                self._hour += 1
                self._minutes = 0
            if self._hour == 24:
                self._day += 1
                self._hour = 0
            sec_c = str(self._seconds)
            min_c = str(self._minutes)
            hou_c = str(self._hour)
            day_c = str(self._day)
            if self._seconds < 10:
                sec_c = '0' + sec_c
            if self._minutes < 10:
                min_c = '0' + min_c
            if self._hour < 10:
                hou_c = '0' + hou_c
            if self._day < 10:
                day_c = '0' + day_c
            # ---------------------------------------------------
            timer = day_c + ' ' + hou_c + ':' + min_c + ':' + sec_c

            # print('Дне ', day_start)
            # print('Час ', hour_start)
            # print('Мин ', minutes_start)
            # print('Сек ', sec_start)
            self.threadTimerSender.emit(timer)
            if self._step == int(sec_to_get) - 1:
                # check_for_import_in_uc()
                self.threadMessageSender.emit(check_for_import_in_uc())
                timer_b = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                timer_a = datetime.datetime.now() + datetime.timedelta(seconds=sec_to_get)
                timer_a = datetime.datetime.strftime(timer_a, '%Y-%m-%d %H:%M:%S')
                self.threadBefore.emit(timer_b)
                self.threadAfter.emit(timer_a)
                self._step = 0
            sec_start -= 1
            time.sleep(1)
        print('Info: Monitoring is stopped')
        configurator.downlog.info('Monitoring is stopped')
        self.threadInfoMessage.emit('Info: Monitoring is stopped')
        self.threadButtonStartE.emit('True')
        self.threadButtonStopD.emit('True')

    def stop(self):
        self._isRunning = False


class Downloader(QThread):
    pre_progress = pyqtSignal(int)
    progress = pyqtSignal(int)
    done = pyqtSignal(str)
    downloading = pyqtSignal(str)

    def __init__(self, file_url, file_name):
        QThread.__init__(self)
        # Флаг инициализации
        self._init = False
        self.fileUrl = file_url
        self.fileName = file_name
        print('Info: Download starting, ' + self.fileUrl)
        configurator.downlog.info('Download starting, ' + self.fileUrl)

    def run(self):
        try:
            configurator.downlog.info('Downloading TSL')
            if configurator.config['Proxy']['proxyon'] == 'Yes':
                proxy = request.ProxyHandler(
                    {'https': 'https://' + configurator.config['Proxy']['ip'] + ':' + configurator.config['Proxy']['port'],
                     'http': 'http://' + configurator.config['Proxy']['ip'] + ':' + configurator.config['Proxy']['port']})
                opener = request.build_opener(proxy)
                request.install_opener(opener)
                configurator.downlog.info('Used proxy')
            request.urlretrieve(self.fileUrl, self.fileName, self._progress)
        except Exception:
            self.done.emit('Ошибка загрузки')
            print('Warning: download failed')
            configurator.downlog.warning('download failed')
        else:
            print('Загрузка завершена')
            configurator.downlog.info('Downloading successfully')
            query_get_settings = Settings.select()
            ver_from_tsl = get_info_xlm('current_version')
            ver = 0
            for settings in query_get_settings:
                ver = settings.value
                break
            if int(ver) == int(ver_from_tsl):
                print('Info: update not need')
                configurator.downlog.info('TSL update not need')
                self.done.emit('Загрузка завершена, обновление не требуется')
            else:
                print('Info: Need update')
                configurator.downlog.info('Need TSL update, new version ' + ver_from_tsl + ', old ' + ver)
                self.done.emit('Загрузка завершена, требуются обновления Базы УЦ и сертификатов. Новая версия '
                               + ver_from_tsl + ' текущая версия ' + ver)
            size_tls = os.path.getsize("tsl.xml")
            self.pre_progress.emit(size_tls)
            self.progress.emit(size_tls)
            self.pre_progress.emit(-1)

    def _progress(self, block_num, block_size, total_size):
        if total_size == -1:
            total_size = int('12000000')
        print(block_num, block_size, total_size)
        self.downloading.emit('Загрузка.')
        if not self._init:
            self.pre_progress.emit(total_size)
            self._init = True
        # Расчет текущего количества данных
        downloaded = block_num * block_size
        if downloaded < total_size:
            # Отправляем промежуток
            self.progress.emit(downloaded)
        else:
            # Чтобы было 100%
            self.progress.emit(total_size)


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        ico = QIcon()
        pixmap_0 = QPixmap()
        pixmap_0.loadFromData(base64.b64decode(base64_icon))
        ico.addPixmap(pixmap_0)
        self.setWindowIcon(QIcon(ico))
        self.window_uc = None
        self.window_crl = None
        self.window_add_crl = None

        self.ui.pushButton_7.pressed.connect(lambda: self.ui.lineEdit.setText(''))
        self.ui.pushButton_8.pressed.connect(lambda: self.ui.lineEdit_2.setText(''))
        self.ui.pushButton_9.pressed.connect(lambda: self.ui.lineEdit_3.setText(''))
        self.ui.pushButton_10.pressed.connect(lambda: self.ui.lineEdit_4.setText(''))
        self.ui.pushButton_11.pressed.connect(lambda: self.ui.lineEdit_5.setText(''))
        self.ui.pushButton_12.pressed.connect(lambda: self.ui.lineEdit_6.setText(''))

        self.tab_uc_sorting = 'asc'
        self.tab_cert_sorting = 'asc'
        self.tab_crl_sorting = 'asc'
        self.sub_tab_watching_crl_sorting = 'asc'
        self.sub_tab_watching_custom_crl_sorting = 'asc'
        self.sub_tab_watching_disabled_crl_sorting = 'asc'

        self.ui.pushButton_61.pressed.connect(lambda: self.tab_uc(self.ui.lineEdit.text(), 'Full_Name', 'sort'))
        self.ui.pushButton_60.pressed.connect(lambda: self.tab_uc(self.ui.lineEdit.text(), 'INN', 'sort'))
        self.ui.pushButton_59.pressed.connect(lambda: self.tab_uc(self.ui.lineEdit.text(), 'OGRN', 'sort'))

        self.ui.pushButton_58.pressed.connect(lambda: self.tab_cert(self.ui.lineEdit_2.text(), 'Name', 'sort'))
        self.ui.pushButton_57.pressed.connect(lambda: self.tab_cert(self.ui.lineEdit_2.text(), 'KeyId', 'sort'))
        self.ui.pushButton_56.pressed.connect(lambda: self.tab_cert(self.ui.lineEdit_2.text(), 'Stamp', 'sort'))
        self.ui.pushButton_55.pressed.connect(lambda: self.tab_cert(self.ui.lineEdit_2.text(), 'SerialNumber', 'sort'))

        self.ui.pushButton_51.pressed.connect(lambda: self.tab_crl(self.ui.lineEdit_3.text(), 'Name', 'sort'))
        self.ui.pushButton_50.pressed.connect(lambda: self.tab_crl(self.ui.lineEdit_3.text(), 'KeyId', 'sort'))
        self.ui.pushButton_49.pressed.connect(lambda: self.tab_crl(self.ui.lineEdit_3.text(), 'Stamp', 'sort'))
        self.ui.pushButton_48.pressed.connect(lambda: self.tab_crl(self.ui.lineEdit_3.text(), 'SerialNumber', 'sort'))
        self.ui.pushButton_53.pressed.connect(lambda: self.tab_crl(self.ui.lineEdit_3.text(), 'UrlCRL', 'sort'))

        self.ui.pushButton_29.pressed.connect(
            lambda: self.sub_tab_watching_crl(self.ui.lineEdit_4.text(), 'Name', 'sort'))
        self.ui.pushButton_28.pressed.connect(
            lambda: self.sub_tab_watching_crl(self.ui.lineEdit_4.text(), 'OGRN', 'sort'))
        self.ui.pushButton_24.pressed.connect(
            lambda: self.sub_tab_watching_crl(self.ui.lineEdit_4.text(), 'KeyId', 'sort'))
        self.ui.pushButton_32.pressed.connect(
            lambda: self.sub_tab_watching_crl(self.ui.lineEdit_4.text(), 'UrlCRL', 'sort'))
        self.ui.pushButton_31.pressed.connect(
            lambda: self.sub_tab_watching_crl(self.ui.lineEdit_4.text(), 'last_download', 'sort'))
        self.ui.pushButton_30.pressed.connect(
            lambda: self.sub_tab_watching_crl(self.ui.lineEdit_4.text(), 'next_update', 'sort'))

        self.ui.pushButton_37.pressed.connect(
            lambda: self.sub_tab_watching_custom_crl(self.ui.lineEdit_5.text(), 'Name', 'sort'))
        self.ui.pushButton_36.pressed.connect(
            lambda: self.sub_tab_watching_custom_crl(self.ui.lineEdit_5.text(), 'OGRN', 'sort'))
        self.ui.pushButton_35.pressed.connect(
            lambda: self.sub_tab_watching_custom_crl(self.ui.lineEdit_5.text(), 'KeyId', 'sort'))
        self.ui.pushButton_34.pressed.connect(
            lambda: self.sub_tab_watching_custom_crl(self.ui.lineEdit_5.text(), 'UrlCRL', 'sort'))
        self.ui.pushButton_40.pressed.connect(
            lambda: self.sub_tab_watching_custom_crl(self.ui.lineEdit_5.text(), 'last_download', 'sort'))
        self.ui.pushButton_39.pressed.connect(
            lambda: self.sub_tab_watching_custom_crl(self.ui.lineEdit_5.text(), 'next_update', 'sort'))

        self.ui.pushButton_44.pressed.connect(
            lambda: self.sub_tab_watching_disabled_crl(self.ui.lineEdit_6.text(), 'Name', 'sort'))
        self.ui.pushButton_43.pressed.connect(
            lambda: self.sub_tab_watching_disabled_crl(self.ui.lineEdit_6.text(), 'OGRN', 'sort'))
        self.ui.pushButton_42.pressed.connect(
            lambda: self.sub_tab_watching_disabled_crl(self.ui.lineEdit_6.text(), 'KeyId', 'sort'))
        self.ui.pushButton_41.pressed.connect(
            lambda: self.sub_tab_watching_disabled_crl(self.ui.lineEdit_6.text(), 'Stamp', 'sort'))
        self.ui.pushButton_47.pressed.connect(
            lambda: self.sub_tab_watching_disabled_crl(self.ui.lineEdit_6.text(), 'SerialNumber', 'sort'))
        self.ui.pushButton_46.pressed.connect(
            lambda: self.sub_tab_watching_disabled_crl(self.ui.lineEdit_6.text(), 'UrlCRL', 'sort'))

        self.ui.lineEdit.textChanged[str].connect(self.tab_uc)
        self.ui.lineEdit_2.textChanged[str].connect(self.tab_cert)
        self.ui.lineEdit_3.textChanged[str].connect(self.tab_crl)
        self.ui.lineEdit_4.textChanged[str].connect(self.sub_tab_watching_crl)
        self.ui.lineEdit_5.textChanged[str].connect(self.sub_tab_watching_custom_crl)
        self.ui.lineEdit_6.textChanged[str].connect(self.sub_tab_watching_disabled_crl)

        self.thread = QThread()
        self.thread_2 = QThread()
        self.thread_3 = QThread()

        self.worker = MainWorker()
        self.worker_2 = CheckCRL()
        self.worker_3 = DownloadAllCRL()

        self.thread.start()
        self.thread_2.start()
        self.thread_3.start()

        self.init_settings()
        self.init_schedule()
        self.tab_info()
        self.tab_uc()
        self.tab_cert()
        self.tab_crl()
        self.tab_watching_crl()
        self.sub_tab_watching_crl()
        self.sub_tab_watching_custom_crl()
        self.sub_tab_watching_disabled_crl()

    def init_schedule(self):
        if configurator.config['Schedule']['allowupdatetslbystart'] == 'Yes':
            self.download_xml()
        if configurator.config['Schedule']['allowupdatecrlbystart'] == 'Yes':
            self.check_all_crl()

    def tab_info(self):
        ucs = UC.select()
        certs = CERT.select()
        crls = CRL.select()
        watching_crl = WatchingCRL.select()
        watching_custom_crl = WatchingCustomCRL.select()
        settings_ver = '0'
        settings_update_date = '0'
        query = Settings.select()
        for data in query:
            if data.name == 'ver':
                settings_ver = data.value
            if data.name == 'data_update':
                settings_update_date = data.value

        self.ui.label_3.setText(" Версия базы: " + settings_ver)
        self.ui.label_2.setText(" Дата выпуска базы: " + settings_update_date.replace('T', ' ').split('.')[0])
        self.ui.label.setText(" Всего УЦ: " + str(ucs.count()))
        self.ui.label_4.setText(" Всего Сертификатов: " + str(certs.count()))
        self.ui.label_5.setText(" Всего CRL: " + str(crls.count()))
        self.ui.label_6.setText(" Мониторится CRL: "
                                + str(int(watching_crl.count())
                                      + int(watching_custom_crl.count())))
        self.ui.pushButton.clicked.connect(self.download_xml)
        self.ui.pushButton.setToolTip('Скачать TSL')
        self.ui.pushButton_2.clicked.connect(self.init_xml)
        self.ui.pushButton_2.setToolTip('Обработать TSL')
        self.ui.pushButton_13.clicked.connect(self.export_crl)
        self.ui.pushButton_13.setToolTip('Экспортировать список CRL')
        self.ui.pushButton_6.pressed.connect(self.import_crl_list)
        self.ui.pushButton_6.setToolTip('Импортировать список CRL')

        watching_crl = WatchingCRL.select().order_by(WatchingCRL.next_update).where(
            WatchingCRL.OGRN == configurator.config['Update']['main_uc_ogrn'])
        self.ui.tableWidget_7.resizeColumnsToContents()
        self.ui.tableWidget_7.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        count = 0
        self.ui.tableWidget_7.setRowCount(watching_crl.count())
        for guc in watching_crl:
            self.ui.tableWidget_7.setItem(count, 0, QTableWidgetItem(str(guc.KeyId)))
            self.ui.tableWidget_7.setItem(count, 1, QTableWidgetItem(str(guc.last_download)))
            self.ui.tableWidget_7.setItem(count, 2, QTableWidgetItem(str(guc.last_update)))
            self.ui.tableWidget_7.setItem(count, 3, QTableWidgetItem(str(guc.next_update)))
            count = count + 1
        self.ui.tableWidget_7.setColumnWidth(1, 180)
        self.ui.tableWidget_7.setColumnWidth(2, 180)
        self.ui.tableWidget_7.setColumnWidth(3, 180)
        self.ui.tableWidget_7.resizeColumnsToContents()
        self.ui.tableWidget_7.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)

        watching_crl = WatchingCRL.select().order_by(WatchingCRL.next_update).where(
            WatchingCRL.OGRN == configurator.config['Update']['self_uc_ogrn'])
        self.ui.tableWidget_8.resizeColumnsToContents()
        self.ui.tableWidget_8.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        count = 0
        self.ui.tableWidget_8.setRowCount(watching_crl.count())
        for you_self in watching_crl:
            self.ui.tableWidget_8.setItem(count, 0, QTableWidgetItem(str(you_self.KeyId)))
            self.ui.tableWidget_8.setItem(count, 1, QTableWidgetItem(str(you_self.last_download)))
            self.ui.tableWidget_8.setItem(count, 2, QTableWidgetItem(str(you_self.last_update)))
            self.ui.tableWidget_8.setItem(count, 3, QTableWidgetItem(str(you_self.next_update)))
            count = count + 1
        self.ui.tableWidget_8.setColumnWidth(1, 180)
        self.ui.tableWidget_8.setColumnWidth(2, 180)
        self.ui.tableWidget_8.setColumnWidth(3, 180)
        self.ui.tableWidget_8.resizeColumnsToContents()
        self.ui.tableWidget_8.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)

        if configurator.config['Logs']['dividelogsbyday'] == 'Yes':
            date_time_day = '_' + datetime.datetime.now().strftime('%Y%m%d')
        else:
            date_time_day = ''

        self.worker.moveToThread(self.thread)

        self.worker.threadTimerSender.connect(lambda y: self.ui.label_36.setText('Время в работе: ' + str(y)))
        self.worker.threadBefore.connect(
            lambda msg: self.ui.label_37.setText('Предыдущее обновление: ' + str(msg)))
        self.worker.threadAfter.connect(lambda msg: self.ui.label_38.setText('Следующее обновление: ' + str(msg)))
        self.worker.threadButtonStartD.connect(lambda: self.ui.pushButton_19.setDisabled(True))
        self.worker.threadButtonStopD.connect(lambda: self.ui.pushButton_20.setDisabled(True))
        self.worker.threadButtonStartE.connect(lambda: self.ui.pushButton_19.setEnabled(True))
        self.worker.threadButtonStopE.connect(lambda: self.ui.pushButton_20.setEnabled(True))
        self.worker.threadInfoMessage.connect(lambda msg: self.ui.label_7.setText(msg))
        self.worker.threadInfoMessage.connect(lambda msg: self.ui.label_7.setText(msg))
        self.worker.threadInfoMessage.connect(lambda msg: self.ui.label_7.setText(msg))
        self.worker.threadMessageSender.connect(lambda msg: self.add_log_to_main_tab(msg))
        #self.worker.threadMessageSender.connect(lambda: self.ui.textBrowser.setText(
        #    open(configurator.config['Folders']['logs'] + '/log' + date_time_day + '.log', 'r').read()))
        #self.worker.threadMessageSender.connect(lambda: self.ui.textBrowser_2.setText(
        #    open(configurator.config['Folders']['logs'] + '/error' + date_time_day + '.log', 'r').read()))
        #self.worker.threadMessageSender.connect(lambda: self.ui.textBrowser_3.setText(
        #    open(configurator.config['Folders']['logs'] + '/download' + date_time_day + '.log', 'r').read()))
        self.worker.threadMessageSender.connect(lambda: self.ui.textBrowser.moveCursor(QTextCursor.End))
        self.worker.threadMessageSender.connect(lambda: self.ui.textBrowser_2.moveCursor(QTextCursor.End))
        self.worker.threadMessageSender.connect(lambda: self.ui.textBrowser_3.moveCursor(QTextCursor.End))
        self.ui.tableWidget_9.setRowCount(1)
        self.ui.tableWidget_9.setItem(0, 1, QTableWidgetItem('Info: init log system'))
        self.ui.tableWidget_9.setColumnWidth(0, 23)
        self.ui.tableWidget_9.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.ui.pushButton_20.clicked.connect(lambda: self.worker.stop() and self.stop_thread)
        self.ui.pushButton_20.setToolTip('Остановить мониторинг CRL')
        self.ui.pushButton_19.clicked.connect(self.worker.task)
        self.ui.pushButton_19.setToolTip('Запустить мониторинг CRL')

    def tab_uc(self, text='', order_by='Full_Name', sort=''):
        if sort == 'sort':
            if order_by == 'Full_Name':
                if self.tab_uc_sorting == 'asc':
                    order = UC.Full_Name.asc()
                    self.tab_uc_sorting = 'desc'
                else:
                    order = UC.Full_Name.desc()
                    self.tab_uc_sorting = 'asc'
            elif order_by == 'INN':
                if self.tab_uc_sorting == 'asc':
                    order = UC.INN.asc()
                    self.tab_uc_sorting = 'desc'
                else:
                    order = UC.INN.desc()
                    self.tab_uc_sorting = 'asc'
            elif order_by == 'OGRN':
                if self.tab_uc_sorting == 'asc':
                    order = UC.OGRN.asc()
                    self.tab_uc_sorting = 'desc'
                else:
                    order = UC.OGRN.desc()
                    self.tab_uc_sorting = 'asc'
            else:
                order = UC.Full_Name.asc()
        else:
            order = UC.Full_Name.asc()

        # order = exec('UC.'+order_by+'.'+sort+'()')

        self.ui.tableWidget.clearContents()
        query = UC.select().order_by(order).where(UC.Registration_Number.contains(text)
                                                  | UC.INN.contains(text)
                                                  | UC.OGRN.contains(text)
                                                  | UC.Name.contains(text)
                                                  | UC.Full_Name.contains(text)).limit(configurator.config['Listing']['uc'])
        count_all = UC.select().where(UC.Registration_Number.contains(text)
                                      | UC.INN.contains(text)
                                      | UC.OGRN.contains(text)
                                      | UC.Name.contains(text)
                                      | UC.Full_Name.contains(text)).limit(configurator.config['Listing']['uc']).count()
        self.ui.tableWidget.setRowCount(count_all)
        count = 0

        for row in query:
            self.ui.tableWidget.setItem(count, 0, QTableWidgetItem(str(row.Full_Name)))
            self.ui.tableWidget.setItem(count, 1, QTableWidgetItem(str(row.INN)))
            self.ui.tableWidget.setItem(count, 2, QTableWidgetItem(str(row.OGRN)))

            button_info = QPushButton()
            button_info.setFixedSize(30, 30)
            icon3 = QIcon()
            pixmap_1 = QPixmap()
            pixmap_1.loadFromData(base64.b64decode(base64_info))
            icon3.addPixmap(pixmap_1)
            button_info.setIcon(icon3)
            button_info.setFlat(True)
            reg_num = row.Registration_Number
            button_info.pressed.connect(lambda rg=reg_num: self.open_sub_window_info_uc(rg))
            button_info.setToolTip('Подробная информация по УЦ')
            self.ui.tableWidget.setCellWidget(count, 3, button_info)
            count = count + 1
        self.ui.tableWidget.resizeColumnsToContents()
        self.ui.tableWidget.setColumnWidth(1, 100)
        self.ui.tableWidget.setColumnWidth(2, 100)
        self.ui.tableWidget.setColumnWidth(3, 31)
        self.ui.tableWidget.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)

    def tab_cert(self, text='', order_by='Name', sort=''):
        if sort == 'sort':
            if order_by == 'Name':
                if self.tab_cert_sorting == 'asc':
                    order = CERT.Name.asc()
                    self.tab_cert_sorting = 'desc'
                else:
                    order = CERT.Name.desc()
                    self.tab_cert_sorting = 'asc'
            elif order_by == 'KeyId':
                if self.tab_cert_sorting == 'asc':
                    order = CERT.KeyId.asc()
                    self.tab_cert_sorting = 'desc'
                else:
                    order = CERT.KeyId.desc()
                    self.tab_cert_sorting = 'asc'
            elif order_by == 'Stamp':
                if self.tab_cert_sorting == 'asc':
                    order = CERT.Stamp.asc()
                    self.tab_cert_sorting = 'desc'
                else:
                    order = CERT.Stamp.desc()
                    self.tab_cert_sorting = 'asc'
            elif order_by == 'SerialNumber':
                if self.tab_cert_sorting == 'asc':
                    order = CERT.SerialNumber.asc()
                    self.tab_cert_sorting = 'desc'
                else:
                    order = CERT.SerialNumber.desc()
                    self.tab_cert_sorting = 'asc'
            else:
                order = CERT.Name.asc()
        else:
            order = CERT.Name.asc()

        self.ui.tableWidget_2.clearContents()

        icon0 = QIcon()
        pixmap_2 = QPixmap()
        pixmap_2.loadFromData(base64.b64decode(base64_file))
        icon0.addPixmap(pixmap_2)
        self.ui.pushButton_22.setIcon(icon0)
        self.ui.pushButton_22.setFlat(True)
        print(configurator.config['Folders']['certs'], os.path.realpath(configurator.config['Folders']['certs']))
        self.ui.pushButton_22.pressed.connect(lambda: os.startfile(os.path.realpath(configurator.config['Folders']['certs'])))
        self.ui.pushButton_22.setToolTip('Открыть папку с сертами')

        query = CERT.select().order_by(order).where(CERT.Registration_Number.contains(text)
                                                    | CERT.Name.contains(text)
                                                    | CERT.KeyId.contains(text)
                                                    | CERT.Stamp.contains(text)
                                                    | CERT.SerialNumber.contains(text)).limit(configurator.config['Listing']['cert'])
        count_all = CERT.select().where(CERT.Registration_Number.contains(text)
                                        | CERT.Name.contains(text)
                                        | CERT.KeyId.contains(text)
                                        | CERT.Stamp.contains(text)
                                        | CERT.SerialNumber.contains(text)).limit(configurator.config['Listing']['cert']).count()
        self.ui.tableWidget_2.setRowCount(count_all)
        count = 0
        for row in query:
            self.ui.tableWidget_2.setItem(count, 0, QTableWidgetItem(str(row.Name)))
            self.ui.tableWidget_2.setItem(count, 1, QTableWidgetItem(str(row.KeyId)))
            self.ui.tableWidget_2.setItem(count, 2, QTableWidgetItem(str(row.Stamp)))
            self.ui.tableWidget_2.setItem(count, 3, QTableWidgetItem(str(row.SerialNumber)))

            button_cert = QPushButton()
            button_cert.setFixedSize(30, 30)
            icon2 = QIcon()
            pixmap_3 = QPixmap()
            pixmap_3.loadFromData(base64.b64decode(base64_diskette))
            icon2.addPixmap(pixmap_3)
            button_cert.setIcon(icon2)
            button_cert.setFlat(True)
            ki = row.KeyId
            # button_cert.pressed.connect(lambda key_id=ki: open_file(key_id, "cer"))
            button_cert.pressed.connect(lambda key_id=ki: save_cert(key_id, configurator.config['Folders']['certs']))
            button_cert.setToolTip('Сохранить сертификат')
            self.ui.tableWidget_2.setCellWidget(count, 4, button_cert)

            button_cert_save = QPushButton()
            button_cert_save.setFixedSize(30, 30)
            icon1 = QIcon()
            pixmap_4 = QPixmap()
            pixmap_4.loadFromData(base64.b64decode(base64_inbox))
            icon1.addPixmap(pixmap_4)
            button_cert_save.setIcon(icon1)
            button_cert_save.setFlat(True)
            ki = row.KeyId
            button_cert_save.pressed.connect(lambda key_id=ki: save_cert(key_id, configurator.config['Folders']['to_uc']))
            button_cert_save.setToolTip('Сохранить сертификат в папку УЦ')
            self.ui.tableWidget_2.setCellWidget(count, 5, button_cert_save)
            count = count + 1
        self.ui.tableWidget_2.setColumnWidth(1, 150)
        self.ui.tableWidget_2.setColumnWidth(2, 150)
        self.ui.tableWidget_2.setColumnWidth(3, 150)
        self.ui.tableWidget_2.setColumnWidth(4, 31)
        self.ui.tableWidget_2.setColumnWidth(5, 31)
        self.ui.tableWidget_2.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)

    def tab_crl(self, text='', order_by='Full_Name', sort=''):
        if sort == 'sort':
            if order_by == 'Name':
                if self.tab_crl_sorting == 'asc':
                    order = CRL.Name.asc()
                    self.tab_crl_sorting = 'desc'
                else:
                    order = CRL.Name.desc()
                    self.tab_crl_sorting = 'asc'
            elif order_by == 'KeyId':
                if self.tab_crl_sorting == 'asc':
                    order = CRL.KeyId.asc()
                    self.tab_crl_sorting = 'desc'
                else:
                    order = CRL.KeyId.desc()
                    self.tab_crl_sorting = 'asc'
            elif order_by == 'Stamp':
                if self.tab_crl_sorting == 'asc':
                    order = CRL.Stamp.asc()
                    self.tab_crl_sorting = 'desc'
                else:
                    order = CRL.Stamp.desc()
                    self.tab_crl_sorting = 'asc'
            elif order_by == 'SerialNumber':
                if self.tab_crl_sorting == 'asc':
                    order = CRL.SerialNumber.asc()
                    self.tab_crl_sorting = 'desc'
                else:
                    order = CRL.SerialNumber.desc()
                    self.tab_crl_sorting = 'asc'
            elif order_by == 'UrlCRL':
                if self.tab_crl_sorting == 'asc':
                    order = CRL.UrlCRL.asc()
                    self.tab_crl_sorting = 'desc'
                else:
                    order = CRL.UrlCRL.desc()
                    self.tab_crl_sorting = 'asc'
            else:
                order = CRL.Name.asc()
        else:
            order = CRL.Name.asc()

        self.ui.tableWidget_3.clearContents()

        icon9 = QIcon()
        pixmap_5 = QPixmap()
        pixmap_5.loadFromData(base64.b64decode(base64_file))
        icon9.addPixmap(pixmap_5)
        self.ui.pushButton_26.setIcon(icon9)
        self.ui.pushButton_26.setFlat(True)
        self.ui.pushButton_26.pressed.connect(lambda: os.startfile(os.path.realpath(configurator.config['Folders']['crls'])))
        self.ui.pushButton_26.setToolTip('Открыть папку с CRL')

        query = CRL.select().order_by(order).where(CRL.Registration_Number.contains(text)
                                                   | CRL.Name.contains(text)
                                                   | CRL.KeyId.contains(text)
                                                   | CRL.Stamp.contains(text)
                                                   | CRL.SerialNumber.contains(text)
                                                   | CRL.UrlCRL.contains(text)).limit(configurator.config['Listing']['crl'])
        count_all = CRL.select().where(CRL.Registration_Number.contains(text)
                                       | CRL.Name.contains(text)
                                       | CRL.KeyId.contains(text)
                                       | CRL.Stamp.contains(text)
                                       | CRL.SerialNumber.contains(text)
                                       | CRL.UrlCRL.contains(text)).limit(configurator.config['Listing']['crl']).count()
        self.ui.tableWidget_3.setRowCount(count_all)
        count = 0
        for row in query:
            self.ui.tableWidget_3.setItem(count, 0, QTableWidgetItem(str(row.Name)))
            self.ui.tableWidget_3.setItem(count, 1, QTableWidgetItem(str(row.KeyId)))
            self.ui.tableWidget_3.setItem(count, 2, QTableWidgetItem(str(row.Stamp)))
            self.ui.tableWidget_3.setItem(count, 3, QTableWidgetItem(str(row.SerialNumber)))
            self.ui.tableWidget_3.setItem(count, 4, QTableWidgetItem(str(row.UrlCRL)))
            button_crl_save = QPushButton()
            button_crl_save.setFixedSize(30, 30)
            icon4 = QIcon()
            pixmap_6 = QPixmap()
            pixmap_6.loadFromData(base64.b64decode(base64_diskette))
            icon4.addPixmap(pixmap_6)
            button_crl_save.setIcon(icon4)
            button_crl_save.setFlat(True)
            button_crl_save.pressed.connect(
                lambda u=row.UrlCRL, s=row.KeyId: download_file(u, s + '.crl', configurator.config['Folders']['crls']))
            button_crl_save.setToolTip('Сохранить CRL')
            self.ui.tableWidget_3.setCellWidget(count, 5, button_crl_save)

            button_crl_save_to_uc = QPushButton()
            button_crl_save_to_uc.setFixedSize(30, 30)
            icon5 = QIcon()
            pixmap_7 = QPixmap()
            pixmap_7.loadFromData(base64.b64decode(base64_inbox))
            icon5.addPixmap(pixmap_7)
            button_crl_save_to_uc.setIcon(icon5)
            button_crl_save_to_uc.setFlat(True)
            button_crl_save_to_uc.pressed.connect(
                lambda u=row.UrlCRL, s=row.KeyId: download_file(u, s + '.crl', configurator.config['Folders']['to_uc']))
            button_crl_save_to_uc.setToolTip('Сохранить CRL в УЦ')
            self.ui.tableWidget_3.setCellWidget(count, 6, button_crl_save_to_uc)

            button_add_to_watch = QPushButton()
            button_add_to_watch.setFixedSize(30, 30)
            icon6 = QIcon()
            pixmap_8 = QPixmap()
            pixmap_8.loadFromData(base64.b64decode(base64_import))
            icon6.addPixmap(pixmap_8)
            button_add_to_watch.setIcon(icon6)
            button_add_to_watch.setFlat(True)
            rb = row.Registration_Number
            ki = row.KeyId
            st = row.Stamp
            sn = row.SerialNumber
            uc = row.UrlCRL
            button_add_to_watch.pressed.connect(lambda registration_number=rb,
                                                keyid=ki,
                                                stamp=st,
                                                serial_number=sn,
                                                url_crl=uc: self.add_watch_current_crl(registration_number,
                                                                                       keyid,
                                                                                       stamp,
                                                                                       serial_number,
                                                                                       url_crl))
            button_add_to_watch.setToolTip('Добавить CRL в мониторинг')
            self.ui.tableWidget_3.setCellWidget(count, 7, button_add_to_watch)
            count = count + 1
        self.ui.tableWidget_3.setColumnWidth(1, 150)
        self.ui.tableWidget_3.setColumnWidth(2, 150)
        self.ui.tableWidget_3.setColumnWidth(3, 150)
        self.ui.tableWidget_3.setColumnWidth(4, 150)
        self.ui.tableWidget_3.setColumnWidth(5, 31)
        self.ui.tableWidget_3.setColumnWidth(6, 31)
        self.ui.tableWidget_3.setColumnWidth(7, 31)
        self.ui.tableWidget_3.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)

    def tab_watching_crl(self):
        self.worker_3.moveToThread(self.thread_3)
        self.ui.pushButton_4.pressed.connect(self.worker_3.task)
        # self.ui.pushButton_4.pressed.connect(self.download_all_crls)
        self.ui.pushButton_4.setToolTip('Скачать все CRL (Занимает значительное время при использовании прокси)')
        self.worker_3.threadInfoMessage.connect(lambda msg: self.ui.label_8.setText(msg))

        # self.ui.pushButton_5.clicked.connect(self.check_all_crl)
        self.ui.pushButton_3.clicked.connect(self.export_crl_to_uc)
        self.ui.pushButton_3.setToolTip('Проверить CRL для копирования в УЦ')

        icon11 = QIcon()
        pixmap_18 = QPixmap()
        pixmap_18.loadFromData(base64.b64decode(base64_file))
        icon11.addPixmap(pixmap_18)
        self.ui.pushButton_27.setIcon(icon11)
        self.ui.pushButton_27.setFlat(True)
        self.ui.pushButton_27.pressed.connect(lambda: os.startfile(os.path.realpath(configurator.config['Folders']['crls'])))
        self.ui.pushButton_27.setToolTip('Открыть папку с CRL')
        self.worker_2.moveToThread(self.thread_2)
        self.ui.pushButton_5.clicked.connect(self.worker_2.task)
        self.ui.pushButton_5.setToolTip('Запустить проверку всех CRL '
                                        '(Занимает значительное время при использовании прокси)')
        self.worker_2.threadInfoMessage.connect(lambda msg: self.ui.label_8.setText(msg))

    def sub_tab_watching_crl(self, text='', order_by='Full_Name', sort=''):
        if sort == 'sort':
            if order_by == 'Name':
                if self.sub_tab_watching_crl_sorting == 'asc':
                    order = WatchingCRL.Name.asc()
                    self.sub_tab_watching_crl_sorting = 'desc'
                else:
                    order = WatchingCRL.Name.desc()
                    self.sub_tab_watching_crl_sorting = 'asc'
            elif order_by == 'OGRN':
                if self.sub_tab_watching_crl_sorting == 'asc':
                    order = WatchingCRL.OGRN.asc()
                    self.sub_tab_watching_crl_sorting = 'desc'
                else:
                    order = WatchingCRL.OGRN.desc()
                    self.sub_tab_watching_crl_sorting = 'asc'
            elif order_by == 'KeyId':
                if self.sub_tab_watching_crl_sorting == 'asc':
                    order = WatchingCRL.KeyId.asc()
                    self.sub_tab_watching_crl_sorting = 'desc'
                else:
                    order = WatchingCRL.KeyId.desc()
                    self.sub_tab_watching_crl_sorting = 'asc'
            elif order_by == 'UrlCRL':
                if self.sub_tab_watching_crl_sorting == 'asc':
                    order = WatchingCRL.UrlCRL.asc()
                    self.sub_tab_watching_crl_sorting = 'desc'
                else:
                    order = WatchingCRL.UrlCRL.desc()
                    self.sub_tab_watching_crl_sorting = 'asc'
            elif order_by == 'last_download':
                if self.sub_tab_watching_crl_sorting == 'asc':
                    order = WatchingCRL.last_download.asc()
                    self.sub_tab_watching_crl_sorting = 'desc'
                else:
                    order = WatchingCRL.last_download.desc()
                    self.sub_tab_watching_crl_sorting = 'asc'
            elif order_by == 'next_update':
                if self.sub_tab_watching_crl_sorting == 'asc':
                    order = WatchingCRL.next_update.asc()
                    self.sub_tab_watching_crl_sorting = 'desc'
                else:
                    order = WatchingCRL.next_update.desc()
                    self.sub_tab_watching_crl_sorting = 'asc'
            else:
                order = WatchingCRL.Name.asc()
        else:
            order = WatchingCRL.Name.asc()

        self.ui.tableWidget_4.clearContents()

        query = WatchingCRL.select().order_by(order).where(WatchingCRL.Name.contains(text)
                                                                      | WatchingCRL.INN.contains(text)
                                                                      | WatchingCRL.OGRN.contains(text)
                                                                      | WatchingCRL.KeyId.contains(text)
                                                                      | WatchingCRL.Stamp.contains(text)
                                                                      | WatchingCRL.SerialNumber.contains(text)
                                                                      | WatchingCRL.UrlCRL.contains(text)). \
            limit(configurator.config['Listing']['watch'])
        count_all = WatchingCRL.select().where(WatchingCRL.Name.contains(text)
                                               | WatchingCRL.INN.contains(text)
                                               | WatchingCRL.OGRN.contains(text)
                                               | WatchingCRL.KeyId.contains(text)
                                               | WatchingCRL.Stamp.contains(text)
                                               | WatchingCRL.SerialNumber.contains(text)
                                               | WatchingCRL.UrlCRL.contains(text)).limit(
            configurator.config['Listing']['watch']).count()
        self.ui.tableWidget_4.setRowCount(count_all)
        count = 0
        brush = QBrush(QColor(0, 255, 0, 255))
        brush.setStyle(Qt.SolidPattern)
        for row in query:
            self.ui.tableWidget_4.setItem(count, 0, QTableWidgetItem(str(row.Name)))
            self.ui.tableWidget_4.setItem(count, 1, QTableWidgetItem(str(row.OGRN)))
            self.ui.tableWidget_4.setItem(count, 2, QTableWidgetItem(str(row.KeyId)))
            self.ui.tableWidget_4.setItem(count, 3, QTableWidgetItem(str(row.UrlCRL)))
            self.ui.tableWidget_4.setItem(count, 4, QTableWidgetItem(str(row.last_download)))
            self.ui.tableWidget_4.setItem(count, 5, QTableWidgetItem(str(row.next_update)))

            if row.status == 'Info: Filetype good':
                status_item = QTableWidgetItem()
                status_icon = QIcon()
                pixmap_9 = QPixmap()
                pixmap_9.loadFromData(base64.b64decode(base64_white_list))
                status_icon.addPixmap(pixmap_9)
                status_item.setIcon(status_icon)
                status_item.setToolTip('Файл прошел проверку')
                self.ui.tableWidget_4.setItem(count, 6, status_item)
            else:
                status_item_2 = QTableWidgetItem()
                status_icon_2 = QIcon()
                pixmap_10 = QPixmap()
                pixmap_10.loadFromData(base64.b64decode(base64_black_list))
                status_icon_2.addPixmap(pixmap_10)
                status_item_2.setIcon(status_icon_2)
                status_item_2.setToolTip('Ошибка в файле или не скачан')
                self.ui.tableWidget_4.setItem(count, 6, status_item_2)

            button_crl_to_uc = QPushButton()
            button_crl_to_uc.setFixedSize(30, 30)
            icon6 = QIcon()
            pixmap_11 = QPixmap()
            pixmap_11.loadFromData(base64.b64decode(base64_inbox))
            icon6.addPixmap(pixmap_11)
            button_crl_to_uc.setIcon(icon6)
            button_crl_to_uc.setFlat(True)
            row_key_id = row.KeyId
            button_crl_to_uc.pressed.connect(lambda rki=row_key_id: copy_crl_to_uc(rki))
            button_crl_to_uc.setToolTip('Копировать CRL в УЦ')
            self.ui.tableWidget_4.setCellWidget(count, 7, button_crl_to_uc)

            button_delete_watch = QPushButton()
            button_delete_watch.setFixedSize(30, 30)
            icon7 = QIcon()
            pixmap_12 = QPixmap()
            pixmap_12.loadFromData(base64.b64decode(base64_export))
            icon7.addPixmap(pixmap_12)
            button_delete_watch.setIcon(icon7)
            button_delete_watch.setFlat(True)
            id_row = row.ID
            button_delete_watch.pressed.connect(lambda o=id_row: self.move_watching_to_passed(o, 'current'))
            button_delete_watch.setToolTip('Убрать CRL из мониторинга')
            self.ui.tableWidget_4.setCellWidget(count, 8, button_delete_watch)
            count = count + 1
        self.ui.tableWidget_4.setColumnWidth(1, 100)
        self.ui.tableWidget_4.setColumnWidth(2, 150)
        self.ui.tableWidget_4.setColumnWidth(3, 150)
        self.ui.tableWidget_4.setColumnWidth(4, 150)
        self.ui.tableWidget_4.setColumnWidth(5, 150)
        self.ui.tableWidget_4.setColumnWidth(6, 25)
        self.ui.tableWidget_4.setColumnWidth(7, 31)
        self.ui.tableWidget_4.setColumnWidth(8, 31)
        self.ui.tableWidget_4.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)

    def sub_tab_watching_custom_crl(self, text='', order_by='Full_Name', sort=''):
        if sort == 'sort':
            if order_by == 'Name':
                if self.sub_tab_watching_custom_crl_sorting == 'asc':
                    order = WatchingCustomCRL.Name.asc()
                    self.sub_tab_watching_custom_crl_sorting = 'desc'
                else:
                    order = WatchingCustomCRL.Name.desc()
                    self.sub_tab_watching_custom_crl_sorting = 'asc'
            elif order_by == 'OGRN':
                if self.sub_tab_watching_custom_crl_sorting == 'asc':
                    order = WatchingCustomCRL.OGRN.asc()
                    self.sub_tab_watching_custom_crl_sorting = 'desc'
                else:
                    order = WatchingCustomCRL.OGRN.desc()
                    self.sub_tab_watching_custom_crl_sorting = 'asc'
            elif order_by == 'KeyId':
                if self.sub_tab_watching_custom_crl_sorting == 'asc':
                    order = WatchingCustomCRL.KeyId.asc()
                    self.sub_tab_watching_custom_crl_sorting = 'desc'
                else:
                    order = WatchingCustomCRL.KeyId.desc()
                    self.sub_tab_watching_custom_crl_sorting = 'asc'
            elif order_by == 'UrlCRL':
                if self.sub_tab_watching_custom_crl_sorting == 'asc':
                    order = WatchingCustomCRL.UrlCRL.asc()
                    self.sub_tab_watching_custom_crl_sorting = 'desc'
                else:
                    order = WatchingCustomCRL.UrlCRL.desc()
                    self.sub_tab_watching_custom_crl_sorting = 'asc'
            elif order_by == 'last_download':
                if self.sub_tab_watching_custom_crl_sorting == 'asc':
                    order = WatchingCustomCRL.last_download.asc()
                    self.sub_tab_watching_custom_crl_sorting = 'desc'
                else:
                    order = WatchingCustomCRL.last_download.desc()
                    self.sub_tab_watching_custom_crl_sorting = 'asc'
            elif order_by == 'next_update':
                if self.sub_tab_watching_custom_crl_sorting == 'asc':
                    order = WatchingCustomCRL.next_update.asc()
                    self.sub_tab_watching_custom_crl_sorting = 'desc'
                else:
                    order = WatchingCustomCRL.next_update.desc()
                    self.sub_tab_watching_custom_crl_sorting = 'asc'
            else:
                order = WatchingCustomCRL.Name.asc()
        else:
            order = WatchingCustomCRL.Name.asc()

        self.ui.tableWidget_5.clearContents()

        self.ui.pushButton_25.pressed.connect(lambda: self.open_sub_window_add())

        query = WatchingCustomCRL.select().order_by(order) \
            .where(WatchingCustomCRL.Name.contains(text)
                   | WatchingCustomCRL.INN.contains(text)
                   | WatchingCustomCRL.OGRN.contains(text)
                   | WatchingCustomCRL.KeyId.contains(text)
                   | WatchingCustomCRL.Stamp.contains(text)
                   | WatchingCustomCRL.SerialNumber.contains(text)
                   | WatchingCustomCRL.UrlCRL.contains(text)). \
            limit(configurator.config['Listing']['watch'])
        count_all = WatchingCustomCRL.select().where(WatchingCustomCRL.Name.contains(text)
                                                     | WatchingCustomCRL.INN.contains(text)
                                                     | WatchingCustomCRL.OGRN.contains(text)
                                                     | WatchingCustomCRL.KeyId.contains(text)
                                                     | WatchingCustomCRL.Stamp.contains(text)
                                                     | WatchingCustomCRL.SerialNumber.contains(text)
                                                     | WatchingCustomCRL.UrlCRL.contains(text)). \
            limit(configurator.config['Listing']['watch']).count()
        # self.ui.tableWidget_5.clear()
        self.ui.tableWidget_5.setRowCount(count_all)
        count = 0
        for row in query:
            self.ui.tableWidget_5.setItem(count, 0, QTableWidgetItem(str(row.Name)))
            self.ui.tableWidget_5.setItem(count, 1, QTableWidgetItem(str(row.OGRN)))
            self.ui.tableWidget_5.setItem(count, 2, QTableWidgetItem(str(row.KeyId)))
            self.ui.tableWidget_5.setItem(count, 3, QTableWidgetItem(str(row.UrlCRL)))
            self.ui.tableWidget_5.setItem(count, 4, QTableWidgetItem(str(row.last_download)))
            self.ui.tableWidget_5.setItem(count, 5, QTableWidgetItem(str(row.next_update)))

            if row.status == 'Info: Filetype good':
                status_item = QTableWidgetItem()
                status_icon = QIcon()
                pixmap_13 = QPixmap()
                pixmap_13.loadFromData(base64.b64decode(base64_white_list))
                status_icon.addPixmap(pixmap_13)
                status_item.setIcon(status_icon)
                status_item.setToolTip('Файл прошел проверку')
                self.ui.tableWidget_5.setItem(count, 6, status_item)
            else:
                status_item_2 = QTableWidgetItem()
                status_icon_2 = QIcon()
                pixmap_14 = QPixmap()
                pixmap_14.loadFromData(base64.b64decode(base64_black_list))
                status_icon_2.addPixmap(pixmap_14)
                status_item_2.setIcon(status_icon_2)
                status_item_2.setToolTip('Ошибка в файле или не скачан')
                self.ui.tableWidget_5.setItem(count, 6, status_item_2)

            button_crl_to_uc = QPushButton()
            button_crl_to_uc.setFixedSize(30, 30)
            icon6 = QIcon()
            pixmap_15 = QPixmap()
            pixmap_15.loadFromData(base64.b64decode(base64_inbox))
            icon6.addPixmap(pixmap_15)
            button_crl_to_uc.setIcon(icon6)
            button_crl_to_uc.setFlat(True)
            row_key_id = row.KeyId
            button_crl_to_uc.pressed.connect(lambda rki=row_key_id: copy_crl_to_uc(rki))
            button_crl_to_uc.setToolTip('Копировать CRL в УЦ')

            # button_crl_to_uc = QPushButton()
            # button_crl_to_uc.setFixedSize(30, 30)
            # button_crl_to_uc.setText("Схр")
            self.ui.tableWidget_5.setCellWidget(count, 7, button_crl_to_uc)

            button_delete_watch = QPushButton()
            button_delete_watch.setFixedSize(30, 30)
            icon8 = QIcon()
            pixmap_16 = QPixmap()
            pixmap_16.loadFromData(base64.b64decode(base64_export))
            icon8.addPixmap(pixmap_16)
            button_delete_watch.setIcon(icon8)
            button_delete_watch.setFlat(True)
            id_row = row.ID
            button_delete_watch.pressed.connect(lambda o=id_row: self.move_watching_to_passed(o, 'custom'))
            button_delete_watch.setToolTip('Убрать CRL из мониторинга')
            self.ui.tableWidget_5.setCellWidget(count, 8, button_delete_watch)

            count = count + 1
        self.ui.tableWidget_5.setColumnWidth(1, 100)
        self.ui.tableWidget_5.setColumnWidth(2, 150)
        self.ui.tableWidget_5.setColumnWidth(3, 150)
        self.ui.tableWidget_5.setColumnWidth(4, 150)
        self.ui.tableWidget_5.setColumnWidth(4, 150)
        self.ui.tableWidget_5.setColumnWidth(5, 150)
        self.ui.tableWidget_5.setColumnWidth(6, 25)
        self.ui.tableWidget_5.setColumnWidth(7, 31)
        self.ui.tableWidget_5.setColumnWidth(8, 31)
        self.ui.tableWidget_5.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)

    def sub_tab_watching_disabled_crl(self, text='', order_by='Full_Name', sort=''):
        if sort == 'sort':
            if order_by == 'Name':
                if self.sub_tab_watching_disabled_crl_sorting == 'asc':
                    order = WatchingDeletedCRL.Name.asc()
                    self.sub_tab_watching_disabled_crl_sorting = 'desc'
                else:
                    order = WatchingDeletedCRL.Name.desc()
                    self.sub_tab_watching_disabled_crl_sorting = 'asc'
            elif order_by == 'OGRN':
                if self.sub_tab_watching_disabled_crl_sorting == 'asc':
                    order = WatchingDeletedCRL.OGRN.asc()
                    self.sub_tab_watching_disabled_crl_sorting = 'desc'
                else:
                    order = WatchingDeletedCRL.OGRN.desc()
                    self.sub_tab_watching_disabled_crl_sorting = 'asc'
            elif order_by == 'KeyId':
                if self.sub_tab_watching_disabled_crl_sorting == 'asc':
                    order = WatchingDeletedCRL.KeyId.asc()
                    self.sub_tab_watching_disabled_crl_sorting = 'desc'
                else:
                    order = WatchingDeletedCRL.KeyId.desc()
                    self.sub_tab_watching_disabled_crl_sorting = 'asc'
            elif order_by == 'Stamp':
                if self.sub_tab_watching_disabled_crl_sorting == 'asc':
                    order = WatchingDeletedCRL.Stamp.asc()
                    self.sub_tab_watching_disabled_crl_sorting = 'desc'
                else:
                    order = WatchingDeletedCRL.Stamp.desc()
                    self.sub_tab_watching_disabled_crl_sorting = 'asc'
            elif order_by == 'SerialNumber':
                if self.sub_tab_watching_disabled_crl_sorting == 'asc':
                    order = WatchingDeletedCRL.SerialNumber.asc()
                    self.sub_tab_watching_disabled_crl_sorting = 'desc'
                else:
                    order = WatchingDeletedCRL.SerialNumber.desc()
                    self.sub_tab_watching_disabled_crl_sorting = 'asc'
            elif order_by == 'UrlCRL':
                if self.sub_tab_watching_disabled_crl_sorting == 'asc':
                    order = WatchingDeletedCRL.UrlCRL.asc()
                    self.sub_tab_watching_disabled_crl_sorting = 'desc'
                else:
                    order = WatchingDeletedCRL.UrlCRL.desc()
                    self.sub_tab_watching_disabled_crl_sorting = 'asc'
            else:
                order = WatchingDeletedCRL.Name.asc()
        else:
            order = WatchingDeletedCRL.Name.asc()

        self.ui.tableWidget_6.clearContents()

        query = WatchingDeletedCRL.select().order_by(order). \
            where(WatchingDeletedCRL.Name.contains(text)
                  | WatchingDeletedCRL.INN.contains(text)
                  | WatchingDeletedCRL.OGRN.contains(text)
                  | WatchingDeletedCRL.KeyId.contains(text)
                  | WatchingDeletedCRL.Stamp.contains(text)
                  | WatchingDeletedCRL.SerialNumber.contains(text)
                  | WatchingDeletedCRL.UrlCRL.contains(text)). \
            limit(configurator.config['Listing']['watch'])
        count_all = WatchingDeletedCRL.select().where(WatchingDeletedCRL.Name.contains(text)
                                                      | WatchingDeletedCRL.INN.contains(text)
                                                      | WatchingDeletedCRL.OGRN.contains(text)
                                                      | WatchingDeletedCRL.KeyId.contains(text)
                                                      | WatchingDeletedCRL.Stamp.contains(text)
                                                      | WatchingDeletedCRL.SerialNumber.contains(text)
                                                      | WatchingDeletedCRL.UrlCRL.contains(text)). \
            limit(configurator.config['Listing']['watch']).count()
        self.ui.tableWidget_6.setRowCount(count_all)
        count = 0
        for row in query:
            self.ui.tableWidget_6.setItem(count, 0, QTableWidgetItem(str(row.Name)))
            self.ui.tableWidget_6.setItem(count, 1, QTableWidgetItem(str(row.OGRN)))
            self.ui.tableWidget_6.setItem(count, 2, QTableWidgetItem(str(row.KeyId)))
            self.ui.tableWidget_6.setItem(count, 3, QTableWidgetItem(str(row.Stamp)))
            self.ui.tableWidget_6.setItem(count, 4, QTableWidgetItem(str(row.SerialNumber)))
            self.ui.tableWidget_6.setItem(count, 5, QTableWidgetItem(str(row.UrlCRL)))

            button_return_watch = QPushButton()
            button_return_watch.setFixedSize(30, 30)
            icon10 = QIcon()
            pixmap_17 = QPixmap()
            pixmap_17.loadFromData(base64.b64decode(base64_import))
            icon10.addPixmap(pixmap_17)
            button_return_watch.setIcon(icon10)
            button_return_watch.setFlat(True)
            id_row = row.ID
            button_return_watch.pressed.connect(lambda o=id_row: self.move_passed_to_watching(o))
            button_return_watch.setToolTip('Вернуть CRL в мониторинг')
            self.ui.tableWidget_6.setCellWidget(count, 6, button_return_watch)
            count = count + 1

        self.ui.tableWidget_6.setColumnWidth(1, 100)
        self.ui.tableWidget_6.setColumnWidth(2, 150)
        self.ui.tableWidget_6.setColumnWidth(3, 150)
        self.ui.tableWidget_6.setColumnWidth(4, 150)
        self.ui.tableWidget_6.setColumnWidth(5, 150)
        self.ui.tableWidget_6.setColumnWidth(6, 31)
        self.ui.tableWidget_6.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)

    def init_settings(self):
        # main config
        self.ui.lineEdit_13.setText(configurator.config['Tabs']['ucLimit'])
        self.ui.lineEdit_18.setText(configurator.config['Tabs']['certLimit'])
        self.ui.lineEdit_17.setText(configurator.config['Tabs']['crlLimit'])
        self.ui.lineEdit_16.setText(configurator.config['Tabs']['wcLimit'])
        self.ui.lineEdit_15.setText(configurator.config['Tabs']['wccLimit'])
        self.ui.lineEdit_14.setText(configurator.config['Tabs']['wcdLimit'])
        self.ui.lineEdit_19.setText(configurator.config['XMPP']['server'])
        self.ui.lineEdit_20.setText(configurator.config['XMPP']['login'])
        self.ui.lineEdit_21.setText(configurator.config['XMPP']['password'])
        self.ui.lineEdit_22.setText(configurator.config['XMPP']['tosend'])
        self.ui.lineEdit_23.setText(configurator.config['Update']['deltaupdateinday'])
        self.ui.lineEdit_24.setText(configurator.config['Update']['timebeforeupdate'])
        self.ui.lineEdit_25.setText(configurator.config['Update']['self_uc_ogrn'])
        self.ui.lineEdit_26.setText(configurator.config['Update']['main_uc_ogrn'])

        if configurator.config['XMPP']['sendinfoerr'] == 'Yes':
            self.ui.checkBox_10.setChecked(True)
        if configurator.config['XMPP']['sendinfonewcrl'] == 'Yes':
            self.ui.checkBox_9.setChecked(True)
        if configurator.config['XMPP']['sendinfonewtsl'] == 'Yes':
            self.ui.checkBox_11.setChecked(True)

        if configurator.config['Sec']['allowImportCRL'] == 'Yes':
            self.ui.checkBox_4.setChecked(True)
        else:
            self.ui.pushButton_6.setDisabled(True)
        if configurator.config['Sec']['allowExportCRL'] == 'Yes':
            self.ui.checkBox_5.setChecked(True)
        else:
            self.ui.pushButton_13.setDisabled(True)
        if configurator.config['Sec']['allowDeleteWatchingCRL'] == 'Yes':
            self.ui.checkBox_6.setChecked(True)
            # self.ui.pushButton_X.setDisabled(True)
        if configurator.config['Sec']['allowDownloadButtonCRL'] == 'Yes':
            self.ui.checkBox_7.setChecked(True)
        else:
            self.ui.pushButton_4.setDisabled(True)
        if configurator.config['Sec']['allowCheckButtonCRL'] == 'Yes':
            self.ui.checkBox_8.setChecked(True)
        else:
            self.ui.pushButton_5.setDisabled(True)

        # Sub  config
        self.ui.lineEdit_12.setText(configurator.config['MainWindow']['height'])
        self.ui.lineEdit_11.setText(configurator.config['MainWindow']['width'])
        self.resize(int(configurator.config['MainWindow']['width']), int(configurator.config['MainWindow']['height']))
        if configurator.config['MainWindow']['savewidth'] == 'No':
            self.ui.checkBox_2.setChecked(True)
        if configurator.config['MainWindow']['allowresize'] == 'Yes':
            self.ui.checkBox_3.setChecked(True)
            self.resize(int(configurator.config['MainWindow']['width']), int(configurator.config['MainWindow']['height']))
            self.setMinimumSize(int(configurator.config['MainWindow']['width']), int(configurator.config['MainWindow']['height']))
            self.setMaximumSize(int(configurator.config['MainWindow']['width']), int(configurator.config['MainWindow']['height']))

        self.ui.comboBox.setCurrentText(configurator.config['Logs']['loglevel'])
        self.ui.spinBox.setValue(int(configurator.config['Logs']['dividelogsbysize']))
        if configurator.config['Logs']['dividelogsbyday'] == 'Yes':
            self.ui.checkBox_14.setChecked(True)
        if configurator.config['Schedule']['allowupdatecrlbystart'] == 'Yes':
            self.ui.checkBox_12.setChecked(True)
        if configurator.config['Schedule']['allowupdatetslbystart'] == 'Yes':
            self.ui.checkBox_13.setChecked(True)
        # download config
        self.ui.label_13.setText(configurator.config['Folders']['crls'])
        self.ui.label_12.setText(configurator.config['Folders']['certs'])
        self.ui.label_11.setText(configurator.config['Folders']['uc'])
        self.ui.label_10.setText(configurator.config['Folders']['tmp'])
        self.ui.label_9.setText(configurator.config['Folders']['to_uc'])

        self.ui.pushButton_18.clicked.connect(lambda: self.choose_directory('crl'))
        self.ui.pushButton_18.setToolTip('Папка загрузки CRL')
        self.ui.pushButton_17.clicked.connect(lambda: self.choose_directory('cert'))
        self.ui.pushButton_17.setToolTip('Папка загрузки сертификатов')
        self.ui.pushButton_16.clicked.connect(lambda: self.choose_directory('uc'))
        self.ui.pushButton_16.setToolTip('Папка загрузки данных УЦ')
        self.ui.pushButton_15.clicked.connect(lambda: self.choose_directory('tmp'))
        self.ui.pushButton_15.setToolTip('Папка загрузки временныйх файлов программы')
        self.ui.pushButton_14.clicked.connect(lambda: self.choose_directory('to_uc'))
        self.ui.pushButton_14.setToolTip('Папка загрузки в УЦ')

        self.ui.lineEdit_7.setText(configurator.config['Proxy']['ip'])
        self.ui.lineEdit_8.setText(configurator.config['Proxy']['port'])
        self.ui.lineEdit_9.setText(configurator.config['Proxy']['login'])
        self.ui.lineEdit_10.setText(configurator.config['Proxy']['password'])

        if configurator.config['Proxy']['proxyon'] == 'No':
            self.ui.checkBox.setChecked(False)
            self.ui.lineEdit_7.setDisabled(True)
            self.ui.lineEdit_8.setDisabled(True)
            self.ui.lineEdit_9.setDisabled(True)
            self.ui.lineEdit_10.setDisabled(True)
        elif configurator.config['Proxy']['proxyon'] == 'Yes':
            self.ui.checkBox.setChecked(True)
            self.ui.lineEdit_7.setEnabled(True)
            self.ui.lineEdit_8.setEnabled(True)
            self.ui.lineEdit_9.setEnabled(True)
            self.ui.lineEdit_10.setEnabled(True)

        # Logs
        if configurator.config['Logs']['dividelogsbyday'] == 'Yes':
            date_time_day = '_' + datetime.datetime.now().strftime('%Y%m%d')
        else:
            date_time_day = ''
        if os.path.exists(configurator.config['Folders']['logs'] + '/log' + date_time_day + '.log'):
            self.ui.textBrowser.setText(
                open(configurator.config['Folders']['logs'] + '/log' + date_time_day + '.log', 'r').read())

        if os.path.exists(configurator.config['Folders']['logs'] + '/error' + date_time_day + '.log'):
            self.ui.textBrowser_2.setText(
                open(configurator.config['Folders']['logs'] + '/error' + date_time_day + '.log', 'r').read())

        if os.path.exists(configurator.config['Folders']['logs'] + '/download' + date_time_day + '.log'):
            self.ui.textBrowser_3.setText(
                open(configurator.config['Folders']['logs'] + '/download' + date_time_day + '.log', 'r').read())

        self.ui.pushButton_21.pressed.connect(lambda: self.save_settings_main())
        self.ui.pushButton_23.pressed.connect(lambda: self.save_settings_sub())

    def save_settings_main(self):
        configurator.set_value_in_property_file('settings.ini', 'Tabs', 'ucLimit', self.ui.lineEdit_13.text())
        configurator.set_value_in_property_file('settings.ini', 'Tabs', 'certLimit', self.ui.lineEdit_18.text())
        configurator.set_value_in_property_file('settings.ini', 'Tabs', 'crlLimit', self.ui.lineEdit_17.text())
        configurator.set_value_in_property_file('settings.ini', 'Tabs', 'wcLimit', self.ui.lineEdit_16.text())
        configurator.set_value_in_property_file('settings.ini', 'Tabs', 'wccLimit', self.ui.lineEdit_15.text())
        configurator.set_value_in_property_file('settings.ini', 'Tabs', 'wcdLimit', self.ui.lineEdit_14.text())
        configurator.set_value_in_property_file('settings.ini', 'MainWindow', 'height', self.ui.lineEdit_12.text())
        configurator.set_value_in_property_file('settings.ini', 'MainWindow', 'width', self.ui.lineEdit_11.text())
        configurator.set_value_in_property_file('settings.ini', 'XMPP', 'server', self.ui.lineEdit_19.text())
        configurator.set_value_in_property_file('settings.ini', 'XMPP', 'login', self.ui.lineEdit_20.text())
        configurator.set_value_in_property_file('settings.ini', 'XMPP', 'password', self.ui.lineEdit_21.text())
        configurator.set_value_in_property_file('settings.ini', 'XMPP', 'tosend', self.ui.lineEdit_22.text())
        configurator.set_value_in_property_file('settings.ini', 'Update', 'deltaupdateinday', self.ui.lineEdit_23.text())
        configurator.set_value_in_property_file('settings.ini', 'Update', 'timebeforeupdate', self.ui.lineEdit_24.text())

        if self.ui.checkBox_10.checkState() == 0:
            configurator.set_value_in_property_file('settings.ini', 'XMPP', 'sendinfoerr', 'No')
        elif self.ui.checkBox_10.checkState() == 2:
            configurator.set_value_in_property_file('settings.ini', 'XMPP', 'sendinfoerr', 'Yes')
        if self.ui.checkBox_9.checkState() == 0:
            configurator.set_value_in_property_file('settings.ini', 'XMPP', 'sendinfonewcrl', 'No')
        elif self.ui.checkBox_9.checkState() == 2:
            configurator.set_value_in_property_file('settings.ini', 'XMPP', 'sendinfonewcrl', 'Yes')
        if self.ui.checkBox_11.checkState() == 0:
            configurator.set_value_in_property_file('settings.ini', 'XMPP', 'sendinfonewtsl', 'No')
        elif self.ui.checkBox_11.checkState() == 2:
            configurator.set_value_in_property_file('settings.ini', 'XMPP', 'sendinfonewtsl', 'Yes')
  
        if self.ui.checkBox_3.checkState() == 0:
            configurator.set_value_in_property_file('settings.ini', 'MainWindow', 'allowresize', 'No')
            self.resize(int(configurator.config['MainWindow']['width']), int(configurator.config['MainWindow']['height']))
            self.setMinimumSize(0, 0)
            self.setMaximumSize(16777215, 16777215)
        elif self.ui.checkBox_3.checkState() == 2:
            configurator.set_value_in_property_file('settings.ini', 'MainWindow', 'allowresize', 'Yes')
            self.resize(int(configurator.config['MainWindow']['width']), int(configurator.config['MainWindow']['height']))
            self.setMinimumSize(int(configurator.config['MainWindow']['width']), int(configurator.config['MainWindow']['height']))
            self.setMaximumSize(int(configurator.config['MainWindow']['width']), int(configurator.config['MainWindow']['height']))

        if self.ui.checkBox_2.checkState() == 0:
            configurator.set_value_in_property_file('settings.ini', 'MainWindow', 'savewidth', 'Yes')
        elif self.ui.checkBox_2.checkState() == 2:
            configurator.set_value_in_property_file('settings.ini', 'MainWindow', 'savewidth', 'No')

        if self.ui.checkBox_4.checkState() == 0:
            configurator.set_value_in_property_file('settings.ini', 'Sec', 'allowImportCRL', 'No')
            self.ui.pushButton_6.setDisabled(True)
        elif self.ui.checkBox_4.checkState() == 2:
            configurator.set_value_in_property_file('settings.ini', 'Sec', 'allowImportCRL', 'Yes')
            self.ui.pushButton_6.setEnabled(True)
        if self.ui.checkBox_5.checkState() == 0:
            configurator.set_value_in_property_file('settings.ini', 'Sec', 'allowExportCRL', 'No')
            self.ui.pushButton_13.setDisabled(True)
        elif self.ui.checkBox_5.checkState() == 2:
            configurator.set_value_in_property_file('settings.ini', 'Sec', 'allowExportCRL', 'Yes')
            self.ui.pushButton_13.setEnabled(True)
        if self.ui.checkBox_6.checkState() == 0:
            configurator.set_value_in_property_file('settings.ini', 'Sec', 'allowDeleteWatchingCRL', 'No')
        elif self.ui.checkBox_6.checkState() == 2:
            configurator.set_value_in_property_file('settings.ini', 'Sec', 'allowDeleteWatchingCRL', 'Yes')
        if self.ui.checkBox_7.checkState() == 0:
            configurator.set_value_in_property_file('settings.ini', 'Sec', 'allowDownloadButtonCRL', 'No')
            self.ui.pushButton_4.setDisabled(True)
        elif self.ui.checkBox_7.checkState() == 2:
            configurator.set_value_in_property_file('settings.ini', 'Sec', 'allowDownloadButtonCRL', 'Yes')
            self.ui.pushButton_4.setEnabled(True)
        if self.ui.checkBox_8.checkState() == 0:
            configurator.set_value_in_property_file('settings.ini', 'Sec', 'allowCheckButtonCRL', 'No')
            self.ui.pushButton_5.setDisabled(True)
        elif self.ui.checkBox_8.checkState() == 2:
            configurator.set_value_in_property_file('settings.ini', 'Sec', 'allowCheckButtonCRL', 'Yes')
            self.ui.pushButton_5.setEnabled(True)
        self.ui.label_27.setText('Настройки сохранены')
        print('Info: save_settings_main::Saved')
        configurator.downlog.info('Save_settings_main::Saved')

    def save_settings_sub(self):
        configurator.set_value_in_property_file('settings.ini', 'Folders', 'certs', self.ui.label_12.text())
        configurator.set_value_in_property_file('settings.ini', 'Folders', 'crls', self.ui.label_13.text())
        configurator.set_value_in_property_file('settings.ini', 'Folders', 'tmp', self.ui.label_10.text())
        configurator.set_value_in_property_file('settings.ini', 'Folders', 'uc', self.ui.label_11.text())
        configurator.set_value_in_property_file('settings.ini', 'Folders', 'to_uc', self.ui.label_9.text())

        configurator.set_value_in_property_file('settings.ini', 'Proxy', 'ip', self.ui.lineEdit_7.text())
        configurator.config['Proxy']['ip'] = self.ui.lineEdit_7.text()
        configurator.set_value_in_property_file('settings.ini', 'Proxy', 'port', self.ui.lineEdit_8.text())
        configurator.config['Proxy']['port'] = self.ui.lineEdit_8.text()
        configurator.set_value_in_property_file('settings.ini', 'Proxy', 'login', self.ui.lineEdit_9.text())
        configurator.config['Proxy']['login'] = self.ui.lineEdit_9.text()
        configurator.set_value_in_property_file('settings.ini', 'Proxy', 'password', self.ui.lineEdit_10.text())
        configurator.config['Proxy']['password'] = self.ui.lineEdit_10.text()

        if self.ui.checkBox_12.checkState() == 0:
            configurator.set_value_in_property_file('settings.ini', 'Schedule', 'allowupdatecrlbystart', 'No')
        elif self.ui.checkBox_12.checkState() == 2:
            configurator.set_value_in_property_file('settings.ini', 'Schedule', 'allowupdatecrlbystart', 'Yes')
        if self.ui.checkBox_13.checkState() == 0:
            configurator.set_value_in_property_file('settings.ini', 'Schedule', 'allowupdatetslbystart', 'No')
        elif self.ui.checkBox_13.checkState() == 2:
            configurator.set_value_in_property_file('settings.ini', 'Schedule', 'allowupdatetslbystart', 'Yes')

        if self.ui.checkBox.checkState() == 0:
            configurator.set_value_in_property_file('settings.ini', 'Proxy', 'proxyon', 'No')
            self.ui.lineEdit_7.setDisabled(True)
            self.ui.lineEdit_8.setDisabled(True)
            self.ui.lineEdit_9.setDisabled(True)
            self.ui.lineEdit_10.setDisabled(True)
        elif self.ui.checkBox.checkState() == 2:
            configurator.set_value_in_property_file('settings.ini', 'Proxy', 'proxyon', 'Yes')
            self.ui.lineEdit_7.setEnabled(True)
            self.ui.lineEdit_8.setEnabled(True)
            self.ui.lineEdit_9.setEnabled(True)
            self.ui.lineEdit_10.setEnabled(True)

        configurator.set_value_in_property_file('settings.ini', 'Logs', 'loglevel', self.ui.comboBox.currentText())
        configurator.set_value_in_property_file('settings.ini', 'Logs', 'dividelogsbysize', str(self.ui.spinBox.value()))
        if self.ui.checkBox_14.checkState() == 0:
            configurator.set_value_in_property_file('settings.ini', 'Logs', 'dividelogsbyday', 'No')
        elif self.ui.checkBox_14.checkState() == 2:
            configurator.set_value_in_property_file('settings.ini', 'Logs', 'dividelogsbyday', 'Yes')
        self.ui.label_28.setText('Настройки сохранены')
        print('Info: save_settings_sub::Saved')
        configurator.downlog.info('Save_settings_sub::Saved')

    def init_xml(self):
        self.ui.pushButton_2.setEnabled(False)
        self.ui.pushButton.setEnabled(False)
        UC.drop_table()
        CRL.drop_table()
        CERT.drop_table()
        UC.create_table()
        CERT.create_table()
        CRL.create_table()
        self.ui.label_7.setText('Обрабатываем данные.')
        configurator.downlog.info('Init TLS started')
        with open('tsl.xml', "rt", encoding="utf-8") as obj:
            xml = obj.read().encode()

        root = etree.fromstring(xml)
        uc_count = 0
        cert_count = 0
        crl_count = 0
        crl_count_all = 3267
        current_version = 'Unknown'
        last_update = 'Unknown'
        self.ui.progressBar_2.setMaximum(100)
        for appt in root.getchildren():
            address_code = ''
            address_name = ''
            address_index = ''
            address_address = ''
            address_street = ''
            address_town = ''
            registration_number = ''
            inn = ''
            ogrn = ''
            full_name = ''
            email = ''
            name = ''
            url = ''
            key_id = ''
            stamp = ''
            serial_number = ''
            cert_base64 = ''
            cert_data = []
            if appt.text:
                if appt.tag == 'Версия':
                    current_version = appt.text
            if appt.text:
                if appt.tag == 'Дата':
                    last_update = appt.text
            for elem in appt.getchildren():
                if not elem.text:
                    for sub_elem in elem.getchildren():
                        if not sub_elem.text:
                            for two_elem in sub_elem.getchildren():
                                if not two_elem.text:
                                    for tree_elem in two_elem.getchildren():
                                        if not tree_elem.text:
                                            if tree_elem.tag == 'Ключ':
                                                data_cert = {}
                                                adr_crl = []
                                                key_ident = {}
                                                for four_elem in tree_elem.getchildren():
                                                    if not four_elem.text:
                                                        for five_elem in four_elem.getchildren():
                                                            if not five_elem.text:
                                                                for six_elem in five_elem.getchildren():
                                                                    if six_elem.text:
                                                                        if six_elem.tag == 'Отпечаток':
                                                                            data_cert['stamp'] = six_elem.text
                                                                        if six_elem.tag == 'СерийныйНомер':
                                                                            cert_count = cert_count + 1
                                                                            data_cert['serrial'] = six_elem.text
                                                                        if six_elem.tag == 'Данные':
                                                                            data_cert['data'] = six_elem.text
                                                            else:
                                                                if five_elem.tag == 'Адрес':
                                                                    five_text = five_elem.text
                                                                    adr_crl.append(five_text)
                                                                    crl_count = crl_count + 1
                                                    else:
                                                        four_text = four_elem.text
                                                        if four_elem.tag == 'ИдентификаторКлюча':
                                                            key_ident['keyid'] = four_text
                                                cert_data.append([key_ident, data_cert, adr_crl])
                                else:
                                    two_text = two_elem.text
                                    if two_elem.tag == 'Код':
                                        address_code = two_text
                                    if two_elem.tag == 'Название':
                                        address_name = two_text
                        else:
                            sub_text = sub_elem.text
                            if sub_elem.tag == 'Индекс':
                                address_index = sub_text
                            if sub_elem.tag == 'УлицаДом':
                                address_street = sub_text
                            if sub_elem.tag == 'Город':
                                address_town = sub_text
                            if sub_elem.tag == 'Страна':
                                address_address = sub_text
                else:
                    text = elem.text
                    if elem.tag == 'Название':
                        full_name = text
                    if elem.tag == 'ЭлектроннаяПочта':
                        email = text
                    if elem.tag == 'КраткоеНазвание':
                        name = text
                    if elem.tag == 'АдресСИнформациейПоУЦ':
                        url = text
                    if elem.tag == 'ИНН':
                        inn = text
                    if elem.tag == 'ОГРН':
                        ogrn = text
                    if elem.tag == 'РеестровыйНомер':
                        registration_number = text
                        uc_count = uc_count + 1
            if registration_number != '':
                self.ui.label_7.setText('Обрабатываем данные: ' + name)
                print(name)
                configurator.downlog.info('Processing - UC:' + name)
                uc = UC(Registration_Number=registration_number,
                        INN=inn,
                        OGRN=ogrn,
                        Full_Name=full_name,
                        Email=email,
                        Name=name,
                        URL=url,
                        AddresCode=address_code,
                        AddresName=address_name,
                        AddresIndex=address_index,
                        AddresAddres=address_address,
                        AddresStreet=address_street,
                        AddresTown=address_town)
                uc.save()
                for cert in cert_data:
                    if type(cert_data) == list:
                        for data in cert:
                            if type(data) == dict:
                                for var, dats in data.items():
                                    if var == 'keyid':
                                        key_id = dats
                                    if var == 'stamp':
                                        stamp = dats
                                    if var == 'serrial':
                                        serial_number = dats
                                    if var == 'data':
                                        cert_base64 = dats

                            if type(data) == list:
                                for dats in data:
                                    url_crl = dats
                                    crl = CRL(Registration_Number=registration_number,
                                              Name=name,
                                              KeyId=key_id,
                                              Stamp=stamp,
                                              SerialNumber=serial_number,
                                              UrlCRL=url_crl)
                                    crl.save()
                    cert = CERT(Registration_Number=registration_number,
                                Name=name,
                                KeyId=key_id,
                                Stamp=stamp,
                                SerialNumber=serial_number,
                                Data=cert_base64)
                    cert.save()

                    # uc_percent_step = int(math.floor(100 / (uc_count_all / uc_count)))
                    # cert_percent_step = int(math.floor(100 / (cert_count_all / cert_count)))
                    crl_percent_step = int(math.floor(100 / (crl_count_all / crl_count)))
                    self.ui.progressBar_2.setValue(crl_percent_step)
        self.ui.label_3.setText(" Версия базы: " + current_version)
        self.ui.label_2.setText(" Дата выпуска базы: " + last_update.replace('T', ' ').split('.')[0])
        self.ui.label.setText(" Всего УЦ: " + str(uc_count))
        self.ui.label_4.setText(" Всего Сертификатов: " + str(cert_count))
        self.ui.label_5.setText(" Всего CRL: " + str(crl_count))

        query_ver = Settings.update(value=current_version).where(Settings.name == 'ver')
        query_ver.execute()
        query_data_update = Settings.update(value=last_update).where(Settings.name == 'data_update')
        query_data_update.execute()
        self.ui.pushButton.setEnabled(True)
        self.ui.pushButton_2.setEnabled(True)
        self.ui.label_7.setText('Готово.')
        configurator.downlog.info('Processing successful done')
        self.ui.progressBar_2.setMaximum(-1)

    def open_sub_window_info_uc(self, reg_number):

        if self.window_uc is None:
            self.window_uc = UcWindow(reg_number)
            self.window_uc.show()
        else:
            self.window_uc.close()  # Close window.
            self.window_uc = None  # Discard reference.

    def open_sub_window_info_crl(self, crl_key_id):

        if self.window_crl is None:
            self.window_crl = CRLWindow(crl_key_id)
            self.window_crl.show()
        else:
            self.window_crl.close()  # Close window.
            self.window_crl = None  # Discard reference.

    def open_sub_window_add(self):

        if self.window_add_crl is None:
            self.window_add_crl = AddCRLWindow()
            self.window_add_crl.show()
        else:
            self.window_add_crl.close()  # Close window.
            self.window_add_crl = None  # Discard reference.

    def choose_directory(self, type_file):

        input_dir = QFileDialog.getExistingDirectory(None, 'Выбор директории:', os.path.expanduser("~"))
        if type_file == 'crl':
            self.ui.label_13.setText(input_dir)
        if type_file == 'cert':
            self.ui.label_12.setText(input_dir)
        if type_file == 'uc':
            self.ui.label_11.setText(input_dir)
        if type_file == 'tmp':
            self.ui.label_10.setText(input_dir)
        if type_file == 'to_uc':
            self.ui.label_9.setText(input_dir)

    def check_all_crl(self):
        query_1 = WatchingCRL.select()
        query_2 = WatchingCustomCRL.select()
        self.ui.pushButton_5.setEnabled(False)
        self.ui.label_8.setText('Проверяем основной список CRL')
        for wc in query_1:
            check_crl(wc.ID, wc.Name, wc.KeyId, wc.UrlCRL)
        self.ui.label_8.setText('Проверяем свой список CRL')
        for wcc in query_2:
            check_custom_crl(wcc.ID, wcc.Name, wcc.KeyId, wcc.UrlCRL)
        self.ui.label_8.setText('Готово')
        self.ui.pushButton_5.setEnabled(True)

    def add_watch_current_crl(self, registration_number, keyid, stamp, serial_number, url_crl):
        count = WatchingCRL.select().where(WatchingCRL.Stamp.contains(stamp)
                                           | WatchingCRL.SerialNumber.contains(serial_number)).count()
        if count < 1:
            select_uc = UC.select().where(UC.Registration_Number == registration_number)
            for row in select_uc:
                add_to_watching_crl = WatchingCRL(Name=row.Name,
                                                  INN=row.INN,
                                                  OGRN=row.OGRN,
                                                  KeyId=keyid,
                                                  Stamp=stamp,
                                                  SerialNumber=serial_number,
                                                  UrlCRL=url_crl,
                                                  status='Unknown',
                                                  download_status='Unknown',
                                                  download_count='0',
                                                  last_download='1970-01-01 00:00:00',
                                                  last_update='1970-01-01 00:00:00',
                                                  next_update='1970-01-01 00:00:00'
                                                  )
                add_to_watching_crl.save()
                self.ui.label_24.setText('Проводится проверка')
                if check_crl(add_to_watching_crl.ID, row.Name, keyid, url_crl) == 'down_error':
                    print('Warning: add_watch_current_crl::crl_added_error:down_error:' + keyid)
                    configurator.downlog.warning('Add_watch_current_crl::crl_added_error:down_error:' + keyid)
                    self.ui.label_24.setText('Ошибка добавления, невозможно скачать файл, проверьте источник')
                else:
                    print('Info: add_watch_current_crl::crl_added:' + keyid)
                    configurator.downlog.info('Info: add_watch_current_crl::crl_added:' + keyid)
                    self.ui.label_24.setText('CRL ' + keyid + ' добавлен в список отлеживания')
        else:
            print('Info: add_watch_current_crl::crl_exist:' + keyid)
            configurator.downlog.info('Info: add_watch_current_crl::crl_exist:' + keyid)
            self.ui.label_24.setText('CRL ' + keyid + ' уже находится в списке отслеживания')

    def add_watch_custom_crl(self, url_crl):
        count = WatchingCustomCRL.select().where(WatchingCustomCRL.UrlCRL.contains(url_crl)).count()
        if count < 1:
            add_to_watching_crl = WatchingCustomCRL(Name='Unknown',
                                                    INN='0',
                                                    OGRN='0',
                                                    KeyId='Unknown',
                                                    Stamp='Unknown',
                                                    SerialNumber='Unknown',
                                                    UrlCRL=url_crl)
            add_to_watching_crl.save()
            self.counter_added_custom = self.counter_added_custom + 1
            print('Info: add_watch_custom_crl::crl_added:' + url_crl)
            configurator.downlog.info('Info: add_watch_custom_crl::crl_added:' + url_crl,)
        else:
            print('Info: add_watch_custom_crl::crl_exist:' + url_crl)
            configurator.downlog.info('Info: add_watch_custom_crl::crl_exist:' + url_crl)
            self.counter_added_exist = self.counter_added_exist + 1
        self.on_changed_find_watching_crl('')

    def add_log_to_main_tab(self, msg):
        msg_list = msg.split(';')[1:]
        for msg in msg_list:
            if not msg == 'NaN':
                button_info_log = QPushButton()
                button_info_log.setFixedSize(23, 23)
                icon12 = QIcon()
                pixmap_19 = QPixmap()
                pixmap_19.loadFromData(base64.b64decode(base64_info))
                icon12.addPixmap(pixmap_19)
                button_info_log.setIcon(icon12)
                button_info_log.setFlat(True)
                key_id = msg.split(' : ')[0]
                button_info_log.pressed.connect(lambda id_key=key_id: self.open_sub_window_info_crl(id_key))
                button_info_log.setToolTip('Подробная информация')
                current_row_count = self.ui.tableWidget_9.rowCount()
                self.ui.tableWidget_9.setRowCount(current_row_count + 1)
                self.ui.tableWidget_9.setCellWidget(current_row_count, 0, button_info_log)
                self.ui.tableWidget_9.setItem(current_row_count, 1, QTableWidgetItem(msg.split(' : ')[1]))
                self.ui.tableWidget_9.scrollToBottom()

    def move_watching_to_passed(self, id_var, from_var):

        if from_var == 'current':
            from_bd = WatchingCRL.select().where(WatchingCRL.ID == id_var)
            for row in from_bd:
                to_bd = WatchingDeletedCRL(Name=row.Name,
                                           INN=row.INN,
                                           OGRN=row.OGRN,
                                           KeyId=row.KeyId,
                                           Stamp=row.Stamp,
                                           SerialNumber=row.SerialNumber,
                                           UrlCRL=row.UrlCRL,
                                           status=row.status,
                                           download_status=row.download_status,
                                           download_count=row.download_count,
                                           last_download=row.last_download,
                                           last_update=row.last_update,
                                           next_update=row.next_update,
                                           moved_from='current')
                to_bd.save()
            WatchingCRL.delete_by_id(id_var)
            self.sub_tab_watching_crl()
            self.sub_tab_watching_disabled_crl()
            print('Info: move_watching_to_passed()::moving_success_current:')
            configurator.downlog.info('Info: move_watching_to_passed()::moving_success_current:')
        elif from_var == 'custom':
            from_bd = WatchingCustomCRL.select().where(WatchingCustomCRL.ID == id_var)
            for row in from_bd:
                to_bd = WatchingDeletedCRL(Name=row.Name,
                                           INN=row.INN,
                                           OGRN=row.OGRN,
                                           KeyId=row.KeyId,
                                           Stamp=row.Stamp,
                                           SerialNumber=row.SerialNumber,
                                           UrlCRL=row.UrlCRL,
                                           status=row.status,
                                           download_status=row.download_status,
                                           download_count=row.download_count,
                                           last_download=row.last_download,
                                           last_update=row.last_update,
                                           next_update=row.next_update,
                                           moved_from='custom')
                to_bd.save()
            WatchingCustomCRL.delete_by_id(id_var)
            self.sub_tab_watching_custom_crl()
            self.sub_tab_watching_disabled_crl()
            print('Info: move_watching_to_passed::moving_success_custom:')
            configurator.downlog.info('Move_watching_to_passed::moving_success_custom:')
        else:
            print('Error: move_watching_to_passed::Error_Moving')
            configurator.downlog.error('Move_watching_to_passed::Error_Moving')

    def move_passed_to_watching(self, id_var):

        from_bd = WatchingDeletedCRL.select().where(WatchingDeletedCRL.ID == id_var)
        for row in from_bd:
            if row.moved_from == 'current':
                to_current = WatchingCRL(Name=row.Name,
                                         INN=row.INN,
                                         OGRN=row.OGRN,
                                         KeyId=row.KeyId,
                                         Stamp=row.Stamp,
                                         SerialNumber=row.SerialNumber,
                                         UrlCRL=row.UrlCRL,
                                         status=row.status,
                                         download_status=row.download_status,
                                         download_count=row.download_count,
                                         last_download=row.last_download,
                                         last_update=row.last_update,
                                         next_update=row.next_update)
                to_current.save()
                WatchingDeletedCRL.delete_by_id(id_var)
                self.sub_tab_watching_disabled_crl()
                self.sub_tab_watching_crl()
                print('Info: move_passed_to_watching()::moving_success_current:')
                configurator.downlog.info('Move_passed_to_watching()::moving_success_current:')
            elif row.moved_from == 'custom':
                to_custom = WatchingCustomCRL(Name=row.Name,
                                              INN=row.INN,
                                              OGRN=row.OGRN,
                                              KeyId=row.KeyId,
                                              Stamp=row.Stamp,
                                              SerialNumber=row.SerialNumber,
                                              UrlCRL=row.UrlCRL,
                                              status=row.status,
                                              download_status=row.download_status,
                                              download_count=row.download_count,
                                              last_download=row.last_download,
                                              last_update=row.last_update,
                                              next_update=row.next_update)
                to_custom.save()
                WatchingDeletedCRL.delete_by_id(id_var)
                self.sub_tab_watching_disabled_crl()
                self.sub_tab_watching_custom_crl()
                print('Info: move_passed_to_watching::moving_success_custom:')
                configurator.downlog.info('Info: move_passed_to_watching::moving_success_custom:')
            else:
                print('Error: move_passed_to_watching::error_moving')
                configurator.downlog.error('move_passed_to_watching::error_moving')

    def download_xml(self):
        self.ui.label_7.setText('Скачиваем список.')
        self.ui.label_7.adjustSize()
        self.ui.pushButton.setEnabled(False)
        self.ui.pushButton_2.setEnabled(False)
        self._download = Downloader(configurator.config['ETrust']['url'], configurator.config['ETrust']['file'])
        self._download.pre_progress.connect(lambda x: self.ui.progressBar.setMaximum(x))
        self._download.progress.connect(lambda y: self.ui.progressBar.setValue(y))
        self._download.downloading.connect(lambda z: self.ui.label_7.setText(z))
        self._download.done.connect(lambda z: self.ui.label_7.setText(z))
        self._download.done.connect(lambda hint1: self.ui.pushButton.setEnabled(True))
        self._download.done.connect(lambda hint2: self.ui.pushButton_2.setEnabled(True))

        self._download.start()

    def download_all_crls(self):
        self.ui.pushButton_4.setEnabled(False)
        query_1 = WatchingCRL.select()
        query_2 = WatchingCustomCRL.select()
        counter_watching_crl_all = WatchingCRL.select().count()
        watching_custom_crl_all = WatchingCustomCRL.select().count()
        counter_watching_crl = 0
        counter_watching_custom_crl = 0
        self.ui.label_8.setText('Загрузка началась')
        for wc in query_1:
            counter_watching_crl = counter_watching_crl + 1
            file_url = wc.UrlCRL
            file_name = wc.KeyId + '.crl'
            # file_name = wc.UrlCRL.split('/')[-1]
            # file_name = wcc.KeyId
            folder = configurator.config['Folders']['crls']
            self.ui.label_8.setText(
                str(counter_watching_crl) + ' из ' + str(counter_watching_crl_all) + ' Загружаем: ' + str(
                    wc.Name) + ' ' + str(wc.KeyId))
            download_file(file_url, file_name, folder, 'current', wc.ID)
            # Downloader(str(wc.UrlCRL), str(wc.SerialNumber)+'.crl')
        print('WatchingCRL downloaded ' + str(counter_watching_crl))
        configurator.downlog.info('WatchingCRL downloaded ' + str(counter_watching_crl))
        for wcc in query_2:
            counter_watching_custom_crl = counter_watching_custom_crl + 1
            file_url = wcc.UrlCRL
            file_name = wcc.KeyId + '.crl'
            # file_name = wcc.UrlCRL.split('/')[-1]
            # file_name = wcc.KeyId
            folder = configurator.config['Folders']['crls']
            self.ui.label_8.setText(
                str(counter_watching_custom_crl) + ' из ' + str(watching_custom_crl_all) + ' Загружаем: ' + str(
                    wcc.Name) + ' ' + str(wcc.KeyId))
            download_file(file_url, file_name, folder, 'custome', wcc.ID)
            # Downloader(str(wcc.UrlCRL), str(wcc.SerialNumber)+'.crl'
        self.ui.label_8.setText('Загрузка закончена')
        print('WatchingCustomCRL downloaded ' + str(counter_watching_custom_crl))
        configurator.downlog.info('WatchingCustomCRL downloaded ' + str(counter_watching_custom_crl))
        print('All download done, w=' + str(counter_watching_crl) + ', c=' + str(counter_watching_custom_crl))
        configurator.downlog.info('All download done, w=' + str(counter_watching_crl) + ', c=' + str(counter_watching_custom_crl))
        self.ui.pushButton_4.setEnabled(True)

    def import_crl_list(self, file_name='crl_list.txt'):

        path = os.path.realpath(file_name)
        if os.path.exists(path):
            crl_list = open(file_name, 'r')
            crl_lists = crl_list.readlines()
            for crl_url in crl_lists:
                crl_url = crl_url.replace("\n", "")
                print(crl_url)
                count = CRL.select().where(CRL.UrlCRL.contains(crl_url)).count()
                data = CRL.select().where(CRL.UrlCRL.contains(crl_url))
                if count > 0:
                    for row in data:
                        print(row.Registration_Number)
                        self.add_watch_current_crl(row.Registration_Number, row.KeyId, row.Stamp, row.SerialNumber,
                                                   row.UrlCRL)
                else:
                    print('add to custom')
                    self.add_watch_custom_crl(crl_url)
                # self.on_changed_find_watching_crl('')
            print(self.counter_added, self.counter_added_custom, self.counter_added_exist)
        else:
            print('Not found crl_list.txt')
            configurator.logg.info('Not found crl_list.txt')

    def export_crl(self):
        self.ui.label_7.setText('Генерируем файл')
        export_all_watching_crl()
        self.ui.label_7.setText('Файл сгенерирован')

    def export_crl_to_uc(self):
        self.ui.pushButton_3.setEnabled(False)
        self.ui.label_8.setText('Обрабатываем CRL для загрузки в УЦ')
        check_for_import_in_uc()
        self.ui.label_8.setText('Все CRL обработаны')
        self.ui.pushButton_3.setEnabled(True)

    def stop_thread(self):
        self.worker.stop()
        self.thread.quit()
        self.thread.wait()


class UcWindow(QWidget):
    def __init__(self, reg_number):
        super().__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.setWindowIcon(QIcon('assists/favicon.ico'))
        self.init(reg_number)

    def init(self, reg_number):

        registration_number = 'Unknown'
        inn = 'Unknown'
        ogrn = 'Unknown'
        full_name = 'Unknown'
        email = 'Unknown'
        name = 'Unknown'
        url = 'Unknown'
        address_code = 'Unknown'
        address_name = 'Unknown'
        address_index = 'Unknown'
        address_address = 'Unknown'
        address_street = 'Unknown'
        address_town = 'Unknown'
        query = UC.select().where(UC.Registration_Number == reg_number)
        for row in query:
            registration_number = 'Регистрационный номер: ' + str(row.Registration_Number)
            inn = 'ИНН: ' + str(row.INN)
            ogrn = 'ОГРН: ' + str(row.OGRN)
            full_name = 'Полное название организации: ' + str(row.Full_Name)
            email = 'Электронная почта: ' + str(row.Email)
            name = 'Название организации: ' + str(row.Name)
            url = 'Интернет адрес: ' + str(row.URL)
            address_code = 'Код региона: ' + str(row.AddresCode)
            address_name = 'Регион: ' + str(row.AddresName)
            address_index = 'Почтовый индекс: ' + str(row.AddresIndex)
            address_address = 'Код страны: ' + str(row.AddresAddres)
            address_street = 'Улица: ' + str(row.AddresStreet)
            address_town = 'Город : ' + str(row.AddresTown)

        self.setWindowTitle(name)
        self.setWindowIcon(QIcon('assists/favicon.ico'))

        self.ui.label_7.setText(registration_number)
        self.ui.label_6.setText(inn)
        self.ui.label_5.setText(ogrn)
        self.ui.label_4.setText(full_name)
        self.ui.label_3.setText(email)
        self.ui.label_2.setText(url)
        self.ui.label.setText(name)

        self.ui.label_13.setText(address_code)
        self.ui.label_12.setText(address_name)
        self.ui.label_11.setText(address_index)
        self.ui.label_10.setText(address_address)
        self.ui.label_8.setText(address_street)
        self.ui.label_9.setText(address_town)

        query = CRL.select().where(CRL.Registration_Number == reg_number)
        query_count = CRL.select().where(CRL.Registration_Number == reg_number).count()
        self.ui.tableWidget.setRowCount(query_count)
        count = 0

        for row in query:
            self.ui.tableWidget.setItem(count, 0, QTableWidgetItem(str(row.Registration_Number)))
            self.ui.tableWidget.setItem(count, 1, QTableWidgetItem(str(row.KeyId)))
            self.ui.tableWidget.setItem(count, 2, QTableWidgetItem(str(row.Stamp)))
            self.ui.tableWidget.setItem(count, 3, QTableWidgetItem(str(row.SerialNumber)))
            self.ui.tableWidget.setItem(count, 4, QTableWidgetItem(str(row.UrlCRL)))
            count = count + 1
        self.ui.tableWidget.setColumnWidth(0, 50)
        self.ui.tableWidget.setColumnWidth(1, 150)
        self.ui.tableWidget.setColumnWidth(2, 150)
        self.ui.tableWidget.setColumnWidth(3, 150)
        self.ui.tableWidget.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)


class CRLWindow(QWidget):
    def __init__(self, crl_key_id):
        super().__init__()
        self.ui_crl = Ui_Form_crl()
        self.ui_crl.setupUi(self)
        self.setWindowIcon(QIcon('assists/favicon.ico'))
        self.init(crl_key_id)

    def init(self, crl_key_id):
        query_1 = WatchingCRL.select().where(WatchingCRL.KeyId == crl_key_id)
        if query_1.count() == 0:
            query_1 = WatchingCustomCRL.select().where(WatchingCustomCRL.KeyId == crl_key_id)
        for wc in query_1:
            self.ui_crl.lineEdit.setText(str(wc.Name))
            self.ui_crl.lineEdit_2.setText(str(wc.INN))
            self.ui_crl.lineEdit_3.setText(str(wc.OGRN))
            self.ui_crl.lineEdit_4.setText(str(wc.KeyId))
            self.ui_crl.lineEdit_5.setText(str(wc.Stamp))
            self.ui_crl.lineEdit_6.setText(str(wc.SerialNumber))
            self.ui_crl.lineEdit_7.setText(str(wc.UrlCRL))
            self.ui_crl.lineEdit_8.setText(str(wc.last_download))
            self.ui_crl.lineEdit_9.setText(str(wc.last_update))
            self.ui_crl.lineEdit_10.setText(str(wc.next_update))


class AddCRLWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.ui_add = Ui_Form_add()
        self.ui_add.setupUi(self)
        self.setWindowIcon(QIcon('assists/favicon.ico'))
        self.ui_add.lineEdit.textChanged[str].connect(self.init)
        self.ui_add.pushButton.pressed.connect(self.set_fields)
        self.ui_add.pushButton_2.pressed.connect(self.query_fields)
        self.init()

    def init(self, text=''):
        self.ui_add.comboBox.clear()
        query = CERT.select().where(CERT.Registration_Number.contains(text)
                                    | CERT.Name.contains(text)
                                    | CERT.KeyId.contains(text)
                                    | CERT.Stamp.contains(text)
                                    | CERT.SerialNumber.contains(text)).limit(configurator.config['Listing']['cert'])
        for row in query:
            self.ui_add.comboBox.addItem(row.Name, row.KeyId)

    def set_fields(self):
        id_cert = self.ui_add.comboBox.currentData()
        query = CERT.select().where(CERT.KeyId == id_cert)
        registration_number = 0
        for row_cert in query:
            registration_number = row_cert.Registration_Number
            self.ui_add.lineEdit_6.setText(str(row_cert.Name))
            self.ui_add.lineEdit_3.setText(str(row_cert.KeyId))
            self.ui_add.lineEdit_8.setText(str(row_cert.Stamp))
            self.ui_add.lineEdit_4.setText(str(row_cert.SerialNumber))
            self.ui_add.lineEdit_5.setText(str(row_cert.Registration_Number))
        query_2 = UC.select().where(UC.Registration_Number == registration_number)
        for row_uc in query_2:
            self.ui_add.lineEdit_7.setText(str(row_uc.INN))
            self.ui_add.lineEdit_2.setText(str(row_uc.OGRN))

    def query_fields(self):
        if CERT.select().where(CERT.KeyId == self.ui_add.lineEdit_3.text()
                               or CERT.Stamp == self.ui_add.lineEdit_8.text()
                               or CERT.SerialNumber == self.ui_add.lineEdit_4.text()).count() > 0:
            if WatchingCRL.select().where(WatchingCRL.KeyId == self.ui_add.lineEdit_3.text()
                                          or WatchingCRL.Stamp == self.ui_add.lineEdit_8.text()
                                          or WatchingCRL.SerialNumber == self.ui_add.lineEdit_4.text()
                                          or WatchingCRL.UrlCRL == self.ui_add.lineEdit_9.text()).count() > 0:
                print('Info: CRL is exists in WatchingCRL')
                configurator.logg.info('CRL is exists in WatchingCRL')
                self.ui_add.label_10.setText('CRL уже есть в основном списке отслеживания')
            elif WatchingCustomCRL.select().where(WatchingCustomCRL.KeyId == self.ui_add.lineEdit_3.text()
                                                  or WatchingCustomCRL.Stamp == self.ui_add.lineEdit_8.text()
                                                  or WatchingCustomCRL.SerialNumber == self.ui_add.lineEdit_4.text()
                                                  or WatchingCustomCRL.UrlCRL == self.ui_add.lineEdit_9.text()) \
                    .count() > 0:
                print('Info: CRL is exist in WatchingCustomCRL')
                configurator.logg.info('Info: CRL is exist in WatchingCustomCRL')
                self.ui_add.label_10.setText('CRL уже есть в своем списке отслеживания')
            elif WatchingDeletedCRL.select().where(WatchingDeletedCRL.KeyId == self.ui_add.lineEdit_3.text()
                                                   or WatchingDeletedCRL.Stamp == self.ui_add.lineEdit_8.text()
                                                   or WatchingDeletedCRL.SerialNumber == self.ui_add.lineEdit_4.text()
                                                   or WatchingDeletedCRL.UrlCRL == self.ui_add.lineEdit_9.text()) \
                    .count() > 0:
                print('Info: CRL is exist in WatchingDeletedCRL')
                configurator.logg.info('CRL is exist in WatchingDeletedCRL')
                self.ui_add.label_10.setText('CRL уже есть в удаленных, или удалите полностью или верните обратно')
            else:
                name = self.ui_add.lineEdit_6.text()
                inn = self.ui_add.lineEdit_7.text()
                ogrn = self.ui_add.lineEdit_2.text()
                key_id = self.ui_add.lineEdit_3.text()
                stamp = self.ui_add.lineEdit_8.text()
                serial_number = self.ui_add.lineEdit_4.text()
                url_crl = self.ui_add.lineEdit_9.text()
                if name == '' or inn == '' or ogrn == '' or key_id == '' or stamp == '' or serial_number == '' or url_crl == '':
                    print('Заполните все поля')
                    print('Info: The fields should not be empty')
                    configurator.logg.info('The fields should not be empty')
                    self.ui_add.label_10.setText('Заполните все поля')
                else:
                    query = WatchingCustomCRL(Name=name,
                                              INN=inn,
                                              OGRN=ogrn,
                                              KeyId=key_id,
                                              Stamp=stamp,
                                              SerialNumber=serial_number,
                                              UrlCRL=url_crl,
                                              status='Unknown',
                                              download_status='Unknown',
                                              download_count='0',
                                              last_download='1970-01-01 00:00:00',
                                              last_update='1970-01-01 00:00:00',
                                              next_update='1970-01-01 00:00:00')
                    query.save()
                    check_custom_crl(query.ID, name, key_id)
                    print('Info: CRL added in WatchingCustomCRL')
                    configurator.logg.info('CRL added in WatchingCustomCRL')
                    self.ui_add.label_10.setText('CRL "' + name + '" добавлен в список отслеживания')
        else:
            print('Warning: Cert not found')
            configurator.logg.warning('Cert not found')
            self.ui_add.label_10.setText('Не найден квалифицированный сертификат УЦ')


if __name__ == "__main__":
    with open(os.path.join(os.getcwd(), 'out.log'), 'w', encoding='utf8') as out:
        with open(os.path.join(os.getcwd(), 'error.log'), 'w', encoding='utf8') as err:
            with redirect_stdout(out), redirect_stderr(err):
                app = QApplication(sys.argv)
                app.setStyle(configurator.config['Style']['window'])
                main_app = MainWindow()
                main_app.show()
                sys.exit(app.exec_())

