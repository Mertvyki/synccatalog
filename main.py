import hashlib
import os
import shutil
import time
import tkinter as tk
import sqlite3
from tkinter.filedialog import askdirectory


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        #Объявляем переменные
        self.text_filed = None
        self.input_source = None
        self.button_sync = None
        self.button_receiver = None
        self.button_source = None
        self.input_receiver = None
        self.cursor = None
        self.conn = None

        #Вызываем функции отрисовки гуи, присоединения бд, и создание таблицы если ее нет
        self.draw_gui()
        self.connect_db()
        self.create_table()

    def draw_gui(self):
        #Задаем размеры формы, запрещаем ей менять размеры, даем название форме
        self.title("Sync")
        self.resizable(False, False)
        self.geometry("400x400")

        #Создаем кнопку для выбора каталога-источника, отрисовываем ее
        self.button_source = tk.Button(text="Выбрать каталог источник",
                                       command=lambda: self.browse_source(self.input_source))
        self.button_source.grid(row=0, column=1, padx=10, pady=10)

        self.button_receiver = tk.Button(text="Выбрать папку приемник",
                                         command=lambda: self.browse_receiver(self.input_receiver))
        self.button_receiver.grid(row=1, column=1, padx=10, pady=10)

        self.button_sync = tk.Button(text="Синхронизировать", command=self.sync_catalog)
        self.button_sync.grid(row=2, column=0, padx=10, pady=10, columnspan=2)

        # Отрисовываем форму ввода пути и блокируем ее изменение
        self.input_source = tk.Entry(state=tk.DISABLED)
        self.input_source.grid(row=0, column=0, padx=10, pady=10)

        self.input_receiver = tk.Entry(state=tk.DISABLED)
        self.input_receiver.grid(row=1, column=0, padx=10, pady=10)

        self.text_filed = tk.Text(height=15, width=40, state=tk.DISABLED)
        self.text_filed.grid(row=3, column=0, padx=10, pady=10, columnspan=2)
    
    def connect_db(self):
        # подключаемся к бд
        self.conn = sqlite3.connect("logs.db")
        self.cursor = self.conn.cursor()

    def create_table(self):
        # создаем таблицу в бд и сохраняем изменения
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS file_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        time DATETIME NOT NULL,
        message TEXT NOT NULL,
        filename TEXT NOT NULL
        )
        ''')
        self.conn.commit()

    def insert_record(self, time, message, filename):
        # вставляем значение в бд
        self.cursor.execute("INSERT INTO file_logs (time, message, filename) VALUES (?, ?, ?)", (time, message, filename))
        self.conn.commit()

    def close_db(self):
        # закрываем подключение к бд
        self.cursor.close()

    def browse_source(self, entry):
        # спрашиваем директорию
        dirname = askdirectory()
        # делаем форму доступной для изменения, удаляем старые значения и вставляем новое, в конце снова блокируем
        entry.configure(state=tk.NORMAL)
        entry.delete(0, tk.END)
        entry.insert(0, dirname)
        entry.configure(state=tk.DISABLED)

    def browse_receiver(self, entry):
        dirname = askdirectory()
        entry.configure(state=tk.NORMAL)
        entry.delete(0, tk.END)
        entry.insert(0, dirname)
        entry.configure(state=tk.DISABLED)

    def text_field_insert(self, text):
        # делаем форму доступной для ввода, вставляем значение и сразу переносим на новую строчку
        self.text_filed.configure(state=tk.NORMAL)
        self.text_filed.insert(tk.END, text + "\n")
        self.text_filed.configure(state=tk.DISABLED)

    def hash_check(self, file_path):
        #Нужна для проверки файла на изменение
        #Создаем объект хэш функции sha256
        hash_func = hashlib.sha256()
        #Открываем файл в режим бинарного чтения
        with open(file_path, "rb") as f:
            #Делаем цикл и присваиваем переменной 8192 байта файла
            while chunk := f.read(8192):
                #Добавляем к объекту хэш функции данные
                hash_func.update(chunk)
        #Возвращаем в 16 формате
        return hash_func.hexdigest()

    def sync_catalog(self):
        # Делаем цикл по  источнику
        for root, _, files in os.walk(self.input_source.get()):
            # Делаем из абсолютного пути относительный, тоесть получаем каталоги и их дочерние каталоги
            rel_path = os.path.relpath(root, self.input_source.get())
            # Присоединяем к каталогу приемнику относительный путь
            dest_path = os.path.join(self.input_receiver.get(), rel_path)
            # Проверем есть ли в каталоге приемнике, каталоги из каталога источника и существует ли каталог приемник
            if not os.path.exists(dest_path) and os.path.exists(self.input_receiver.get()):
                # Создаем каталоги
                os.mkdir(dest_path)
                # Выводим лог о создании каталога
                self.text_field_insert(f"{time.strftime("%H:%M:%S")} Добавлена папка {rel_path}")
                # Добавляем в бд запись о создании каталога
                self.insert_record(time.strftime("%H:%M:%S"), "Добавлена папка", rel_path)
            # Цикл по файлам из каталога исчтоника
            for file in files:
                # Создаем путь до файла
                dest_file_path = os.path.join(dest_path, file)
                # Создаем путь до файла в каталоге источнике
                source_file_path = os.path.join(root, file)
                # Проверяем есть ли файл в каталоге приемнике
                if not os.path.exists(dest_file_path) and os.path.exists(self.input_receiver.get()):
                    # Копируем файлы из источника в приемник
                    shutil.copy2(source_file_path, dest_file_path)
                    self.text_field_insert(f"{time.strftime("%H:%M:%S")} Добавлен файл {file}")
                    self.insert_record(time.strftime("%H:%M:%S"), "Добавлен файл", file)
                # Если файл уже есть в приемнике, то сравниваем их хэши, если они разные то файл был изменен
                elif self.hash_check(source_file_path) != self.hash_check(dest_file_path):
                    shutil.copy2(source_file_path, dest_file_path)
                    self.text_field_insert(f"{time.strftime("%H:%M:%S")} Изменен файл {file}")
                    self.insert_record(time.strftime("%H:%M:%S"), "Изменен файл", file)
        # Цикл по приемнику для удаления файлов и каталогов
        for root, _, files in os.walk(self.input_receiver.get()):
            rel_path = os.path.relpath(root, self.input_receiver.get())
            # Присоединяем к каталогу источнику относительный путь
            dest_path = os.path.join(self.input_source.get(), rel_path)
            # Проверяем есть ли каталоги приемника в источнике
            if not os.path.exists(dest_path) and os.path.exists(self.input_source.get()):
                # Если нет такого каталога, удаляем его в источнике
                shutil.rmtree(os.path.join(root))
                self.text_field_insert(f"{time.strftime("%H:%M:%S")} Удалена папка {rel_path}")
                self.insert_record(time.strftime("%H:%M:%S"), "Удалена папка", rel_path)
            for file in files:
                dest_file_path = os.path.join(dest_path, file)
                source_file_path = os.path.join(root, file)
                # Проверяем есть ли файл из приемника, в источнике и существует ли каталог в котором находится файл
                if not os.path.exists(dest_file_path) and os.path.exists(dest_path):
                    # Удаляем файл
                    os.remove(source_file_path)
                    self.text_field_insert(f"{time.strftime("%H:%M:%S")} Удален файл {file}")
                    self.insert_record(time.strftime("%H:%M:%S"), "Удален файл", file)



if __name__ == "__main__":
    app = App()
    app.mainloop()
    app.close_db()