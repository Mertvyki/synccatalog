import hashlib
import os
import shutil
import tkinter as tk
from tkinter.filedialog import askdirectory

from docutils.nodes import entry


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sync")
        self.resizable(False, False)
        self.geometry("400x400")
        self.button_source = tk.Button(text="Выбрать каталог источник", command= lambda: self.browse_source(self.input_source))
        self.button_source.grid(row=0, column=1, padx=10, pady=10)
        self.button_receiver = tk.Button(text="Выбрать папку приемник", command= lambda: self.browse_receiver(self.input_receiver))
        self.button_receiver.grid(row=1, column=1, padx=10, pady=10)
        self.button_sync = tk.Button(text="Синхронизировать", command=self.sync_catalog)
        self.button_sync.grid(row=2, column=0, padx=10, pady=10, columnspan=2)
        self.input_source = tk.Entry()
        self.input_source.grid(row=0, column=0, padx=10, pady=10)
        self.input_receiver = tk.Entry()
        self.input_receiver.grid(row=1, column=0, padx=10, pady=10)

    def browse_source(self, entry):
        dirname = askdirectory()
        entry.delete(0, tk.END)
        entry.insert(0, dirname)

    def browse_receiver(self, entry):
        dirname = askdirectory()
        entry.delete(0, tk.END)
        entry.insert(0, dirname)

    def hash_check(self, file_path):
        hash_func = hashlib.sha256()
        with open(file_path, "rb") as f:
            while chunk := f.read(8192):
                hash_func.update(chunk)
        return hash_func.hexdigest()

    def sync_catalog(self):
        for root, _, files in os.walk(self.input_source.get()):
            rel_path = os.path.relpath(root, self.input_source.get())
            dest_path = os.path.join(self.input_receiver.get(), rel_path)
            if not os.path.exists(dest_path):
                os.mkdir(dest_path)
            for file in files:
                dest_file_path = os.path.join(dest_path, file)
                source_file_path = os.path.join(root, file)
                if not os.path.exists(dest_file_path):
                    shutil.copy2(source_file_path, dest_file_path)
                elif self.hash_check(source_file_path) != self.hash_check(dest_file_path):
                    shutil.copy2(source_file_path, dest_file_path)
        for root, _, files in os.walk(self.input_receiver.get()):
            rel_path = os.path.relpath(root, self.input_receiver.get())
            dest_path = os.path.join(self.input_source.get(), rel_path)
            if not os.path.exists(dest_path):
                shutil.rmtree(os.path.join(root, rel_path))
            for file in files:
                dest_file_path = os.path.join(dest_path, file)
                if not os.path.exists(dest_file_path):
                    print(dest_file_path)



if __name__ == "__main__":
    app = App()
    app.mainloop()