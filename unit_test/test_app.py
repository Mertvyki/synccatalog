import os
import shutil
import sys
import unittest

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, '..'))
from main import App
from unittest.mock import MagicMock


class SyncCatalogTestCase(unittest.TestCase):
    #Задаем фикстуру для начальных значений
    def setUp(self):
        self.app = App()
        self.full_path = os.path.dirname(os.path.abspath(__file__))
        self.source_path = os.path.join(self.full_path, "test_source")
        self.receiver_path = os.path.join(self.full_path,"test_receiver")

        os.makedirs(self.source_path, exist_ok=True)
        os.makedirs(self.receiver_path, exist_ok=True)

        self.app.input_source = MagicMock()
        self.app.input_source.get.return_value = self.source_path

        self.app.input_receiver = MagicMock()
        self.app.input_receiver.get.return_value = self.receiver_path

    #Проверка синхронизации нового файла
    def test_sync_new_file(self):
        #Создаем файл в источнике
        with open(os.path.join(self.source_path, "test_new_file.txt"), "w") as f:
            f.write("test content")

        #Выполняем синхронизацию
        self.app.sync_catalog()

        # Проверяем возвращает ли True os.path.exists(True если путь до файла правильный)
        self.assertTrue(os.path.exists(os.path.join(self.receiver_path, "test_new_file.txt")))

    def test_sync_modified_file(self):
        with open(os.path.join(self.source_path, "test_modified_file.txt"), "w") as f:
            f.write("test content")

        self.app.sync_catalog()

        #Изменяем файл
        with open(os.path.join(self.source_path, "test_modified_file.txt"), "w") as f:
            f.write("test modified")

        self.app.sync_catalog()

        #Открываем файл в приемнике
        with open(os.path.join(self.receiver_path, "test_modified_file.txt"), "r") as f:
            #Читаем файл
            content = f.read()
        #Сравниваем значение файла
        self.assertEqual(content, "test modified")

    def test_sync_deleted_file(self):
        with open(os.path.join(self.source_path, "test_deleted_file.txt"), "w") as f:
            f.write("test content")

        self.app.sync_catalog()

        #Удаляем файл в источнике
        os.remove(os.path.join(self.source_path, "test_deleted_file.txt"))

        self.app.sync_catalog()

        #Проверяем возвращает ли False os.path.exists
        self.assertFalse(os.path.exists(os.path.join(self.receiver_path, "test_deleted_file.txt")))

    def tearDown(self):
        #После тестов удаляем созданные тестовые каталоги
        shutil.rmtree(self.source_path, ignore_errors=True)
        shutil.rmtree(self.receiver_path, ignore_errors=True)
        #Закрываем приложение
        self.app.destroy()


if __name__ == '__main__':
    unittest.main()