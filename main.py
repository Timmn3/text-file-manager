import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTextEdit, QFileDialog, QInputDialog, QMessageBox
)
from PyQt6.QtCore import Qt
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
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        # Верхний раздел: список файлов и текстовый редактор
        self.top_layout = QHBoxLayout()
        self.layout.addLayout(self.top_layout)

        self.file_list_widget = QWidget()
        self.file_list_layout = QVBoxLayout()
        self.file_list_widget.setLayout(self.file_list_layout)
        self.top_layout.addWidget(self.file_list_widget)

        self.editor = QTextEdit()
        self.top_layout.addWidget(self.editor)

        # Нижний раздел: кнопки
        self.bottom_layout = QHBoxLayout()
        self.layout.addLayout(self.bottom_layout)

        # Кнопки
        # Кнопки
        self.select_folder_button = QPushButton("Выбрать папку")
        self.select_folder_button.clicked.connect(self.select_folder)
        self.select_folder_button.setStyleSheet("""
            QPushButton {
                background-color: #007BFF;  /* Синий цвет */
                color: white;
                border-radius: 10px;
                font-size: 16px;
                padding: 10px;
                border: none;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #0056b3; /* Темно-синий цвет */
            }
        """)
        self.bottom_layout.addWidget(self.select_folder_button)

        self.new_file_button = QPushButton("Создать новый файл")
        self.new_file_button.clicked.connect(self.create_new_file)
        self.new_file_button.setStyleSheet("""
            QPushButton {
                background-color: #007BFF;  /* Синий цвет */
                color: white;
                border-radius: 10px;
                font-size: 16px;
                padding: 10px;
                border: none;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #0056b3; /* Темно-синий цвет */
            }
        """)
        self.bottom_layout.addWidget(self.new_file_button)

        # Список файлов
        self.files = {}
        self.current_file = None

        self.init_ui()

        # Стилизация интерфейса
        self.set_styles()

    def init_ui(self):
        if self.default_path:
            self.load_files(self.default_path)

    def set_styles(self):
        """Стилизация интерфейса с использованием QSS."""
        self.setStyleSheet("""
            QWidget {
                background-color: #f2f2f2;
                font-family: Arial, sans-serif;
                font-size: 16px;
            }
            QPushButton {
                background-color: #4CAF50; /* Светло-зеленый */
                color: white;
                border-radius: 10px;
                font-size: 16px;
                padding: 10px;
                border: none;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #45a049; /* Темно-зеленый при наведении */
            }
            QPushButton:disabled {
                background-color: #ccc;
            }
            QTextEdit {
                border: 2px solid #ccc;
                border-radius: 10px;
                padding: 8px;
                font-size: 16px;
                background-color: white;
            }
        """)

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
            if isinstance(widget, QPushButton):
                self.file_list_layout.removeWidget(widget)
                widget.deleteLater()

        for file_name in sorted(f for f in os.listdir(folder) if f.endswith(".txt")):
            full_path = os.path.join(folder, file_name)
            with open(full_path, "r", encoding="utf-8") as f:
                self.files[file_name] = f.read()

            button = QPushButton(file_name[:-4])
            button.clicked.connect(lambda _, name=file_name: self.open_file(name))
            self.file_list_layout.addWidget(button)

    def open_file(self, file_name):
        self.current_file = file_name
        self.editor.setPlainText(self.files[file_name])

    def create_new_file(self):
        file_name, ok = QInputDialog.getText(self, "Создать новый файл", "Введите имя файла:")
        if ok and file_name.strip():
            file_name = file_name.strip()
            full_path = os.path.join(self.default_path, f"{file_name}.txt")
            if os.path.exists(full_path):
                QMessageBox.warning(self, "Ошибка", "Файл с таким именем уже существует!")
            else:
                with open(full_path, "w", encoding="utf-8") as f:
                    f.write("")
                self.files[f"{file_name}.txt"] = ""
                self.load_files(self.default_path)

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
