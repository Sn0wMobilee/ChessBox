import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from Gui.main_menu import LoginWindow
from Engine.utils import resource_path
# Функция для корректного поиска файлов внутри .exe

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Устанавливаем иконку для приложения
    icon_path = resource_path("icon.ico")
    app.setWindowIcon(QIcon(icon_path))
    
    window = LoginWindow()
    sys.exit(app.exec())