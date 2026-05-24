import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from Gui.main_menu import LoginWindow
from Gui.main_menu import GameMenuWindow 
from DataBase.database import Database 
from DataBase.session import load_session
from Engine.utils import resource_path

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Устанавливаем иконку для всего приложения
    icon_path = resource_path("icon.ico")
    app.setWindowIcon(QIcon(icon_path))
    
    # Проверяем, есть ли сохраненный пользователь на диске
    saved_user = load_session()
    auto_login_success = False
    
    if saved_user:
        print(f"[Main] Найдена сессия для пользователя: {saved_user}")
        db = Database()
        # Проверяем пользователя через вашу базу данных
        success, result = db.auto_login(saved_user)
        print(f"[Main] Результат авто-входа: {success}, {result}")
        
        if success:
            auto_login_success = True
            # Если всё ок, создаем и сразу показываем игровое меню
            window = GameMenuWindow(saved_user)
            window.show()
            
    # Если авто-вход не удался или сессии не было, открываем окно логина
    if not auto_login_success:
        print("[Main] Сессия не найдена. Открываем окно входа.")
        window = LoginWindow()
        window.show()
        
    # Запускаем главный цикл обработки событий PyQt
    sys.exit(app.exec())