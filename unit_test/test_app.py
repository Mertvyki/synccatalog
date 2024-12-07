import os
import unittest
from main import App


class SyncCatalogTestCase(unittest.TestCase):
    def setUp(self):
        self.app = App()
        self.source_path = "test_source"
        self.receiver_path = "test_receiver"
        os.makedirs(self.source_path, exist_ok=True)
        os.makedirs(self.receiver_path, exist_ok=True)
        self.app.input_source.insert(0, self.source_path)
        self.app.input_receiver.insert(0, self.receiver_path)

    def test_browse_source(self):
        self.assertEqual(self.source_path, self.app.input_source.get())

    def test_browse_receiver(self):
        self.assertEqual(self.receiver_path, self.app.input_receiver.get())

    def test_sync_new_file(self):
        with open(os.path.join(self.source_path, "test_new_file.txt"), "w") as f:
            f.write("test content")
        self.app.sync_catalog()
        self.assertTrue(os.path.exists(os.path.join(self.receiver_path, "test_new_file.txt")))

    def test_sync_modified_file(self):
        with open(os.path.join(self.source_path, "test_modified_file.txt"), "w") as f:
            f.write("test content")

        self.app.sync_catalog()

        with open(os.path.join(self.source_path, "test_modified_file.txt"), "w") as f:
            f.write("test modified")

        self.app.sync_catalog()

        with open(os.path.join(self.source_path, "test_modified_file.txt"), "r") as f:
            content = f.read()
        self.assertEqual(content, "test modified")

    def test_sync_deleted_file(self):
        with open(os.path.join(self.source_path, "test_deleted_file.txt"), "w") as f:
            f.write("test content")

        self.app.sync_catalog()

        os.remove(os.path.join(self.source_path, "test_deleted_file.txt"))

        self.app.sync_catalog()

        self.assertFalse(os.path.exists(os.path.join(self.receiver_path, "test_deleted_file.txt")))


if __name__ == '__main__':
    unittest.main()