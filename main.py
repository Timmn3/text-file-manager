import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTextEdit, QFileDialog, QLineEdit, QLabel
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

import json


# Файл для сохранения пути
CONFIG_FILE = "config.json"


def save_config(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f)


def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {}


class TxtViewerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Txt Viewer")
        self.resize(800, 600)

        # Загрузка пути по умолчанию
        self.config = load_config()
        self.default_path = self.config.get("default_path", "")

        # Основной интерфейс
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QHBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.file_list_widget = QWidget()
        self.file_list_layout = QVBoxLayout()
        self.file_list_widget.setLayout(self.file_list_layout)
        self.layout.addWidget(self.file_list_widget)

        self.editor = QTextEdit()
        self.layout.addWidget(self.editor)

        # Список файлов
        self.files = {}
        self.current_file = None

        self.init_ui()

    def init_ui(self):
        # Кнопка для выбора папки
        self.select_folder_button = QPushButton("Выбрать папку")
        self.select_folder_button.clicked.connect(self.select_folder)
        self.file_list_layout.addWidget(self.select_folder_button)

        # Кнопка для создания нового файла
        self.new_file_button = QPushButton("Создать новый файл")
        self.new_file_button.setStyleSheet("background-color: lightblue;")
        self.new_file_button.clicked.connect(self.create_new_file)
        self.file_list_layout.addWidget(self.new_file_button)

        self.new_file_input = QLineEdit()
        self.file_list_layout.addWidget(self.new_file_input)

        if self.default_path:
            self.load_files(self.default_path)

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Выберите папку", self.default_path or os.getcwd())
        if folder:
            self.default_path = folder
            self.config["default_path"] = folder
            save_config(self.config)
            self.load_files(folder)

    def load_files(self, folder):
        self.files.clear()
        for i in reversed(range(self.file_list_layout.count())):
            widget = self.file_list_layout.itemAt(i).widget()
            if isinstance(widget, QPushButton) and widget not in {self.select_folder_button, self.new_file_button}:
                self.file_list_layout.removeWidget(widget)
                widget.deleteLater()

        for file_name in sorted(f for f in os.listdir(folder) if f.endswith(".txt")):
            full_path = os.path.join(folder, file_name)
            with open(full_path, "r", encoding="utf-8") as f:
                self.files[file_name] = f.read()

            button = QPushButton(file_name[:-4])
            button.setStyleSheet("background-color: lightgreen;")
            button.clicked.connect(lambda _, name=file_name: self.open_file(name))
            self.file_list_layout.addWidget(button)

    def open_file(self, file_name):
        self.current_file = file_name
        self.editor.setPlainText(self.files[file_name])

    def create_new_file(self):
        file_name = self.new_file_input.text().strip()
        if not file_name:
            return

        full_path = os.path.join(self.default_path, f"{file_name}.txt")
        if not os.path.exists(full_path):
            with open(full_path, "w", encoding="utf-8") as f:
                f.write("")
            self.files[f"{file_name}.txt"] = ""
            self.load_files(self.default_path)
            self.new_file_input.clear()

    def closeEvent(self, event):
        # Сохранение изменений
        if self.current_file and self.current_file in self.files:
            self.files[self.current_file] = self.editor.toPlainText()

        for file_name, content in self.files.items():
            full_path = os.path.join(self.default_path, file_name)
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)

        event.accept()


def main():
    app = QApplication(sys.argv)
    window = TxtViewerApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
