import os
import unittest
import logging
from configurator import configurator
from configurator import BASE_DIR


class TestConfig(unittest.TestCase):
    def setUp(self) -> None:
        self.config = configurator.config
        return super().setUp()

    def test_one_absent_key(self):
        self.assertIn('formatter_mainform', self.config)
        del self.config['formatter_mainform']['datefmt']
        self.assertNotIn('datefmt', self.config['formatter_mainform'])
        configurator.write_configuration()
        configurator.configure()
        self.assertIn('datefmt', self.config['formatter_mainform'])


class TestFoldersConfig(unittest.TestCase):
    def setUp(self) -> None:
        self.config = configurator.config
        return super().setUp()

    def test_folders_section_exists(self):
        self.assertIn('Folders', self.config)

    def test_base_dir_section_exists(self):
        self.assertIn('BaseDir', self.config)

    def test_folders_exists(self):
        for path in self.config['Folders'].values():
            print(path, os.path.abspath(path), os.path.join(BASE_DIR, path))
            self.assertTrue(os.path.exists(os.path.abspath(path)))


class TestLogConfig(unittest.TestCase):
    def setUp(self) -> None:
        self.config = configurator.config
        # Если путь в Windows будет содержать *\G*, то может выскочить сообщение
        # <string>:1: DeprecationWarning: invalid escape sequence \G
        #logging.config.fileConfig(self.config)
        return super().setUp()

    def test_loggers_sections_exists(self):
        self.assertIn('loggers', self.config)
        self.assertIn('formatters', self.config)
        self.assertIn('handlers', self.config)
        self.assertIn('logger_root', self.config)
        self.assertIn('logger_download', self.config)
        self.assertIn('formatter_mainform', self.config)
        self.assertIn('handler_logrotate', self.config)
        self.assertIn('handler_updfile', self.config)

    def test_loggers(self):
        #logg = logging.getLogger()
        configurator.logg.info('logger is ready @@@')
        #downlog = logging.getLogger('downlog')
        configurator.downlog.error('test error @@@')
        with open(eval(self.config['handler_logrotate']['args'])[0], 'r', encoding='utf8') as filelog:
            strin_list = filelog.readlines()
            self.assertIn('logger is ready @@@', strin_list[-2])
            self.assertIn('test error @@@', strin_list[-1])
        with open(eval(self.config['handler_updfile']['args'])[0], 'r', encoding='utf8') as filelog:
            strin_list = filelog.readlines()
            self.assertIn('test error @@@', strin_list[-1])
        print(configurator.logg.handlers, configurator.logg.handlers[0].formatter, configurator.logg.handlers[0].name)
        print(configurator.downlog.handlers, configurator.downlog.handlers[0].formatter, configurator.downlog.handlers[0].name)

    



if __name__ == '__main__':
    unittest.main()