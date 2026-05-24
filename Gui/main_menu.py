from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
import os
import sys
from DataBase.database import Database
from Gui.chessgame import ChessWindow
from DataBase.session import load_session, clear_session, save_session
from Network.network import P2PNetwork
from Engine.utils import resource_path

class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Устанавливаем иконку для окна
        icon_path = resource_path("icon.ico")
        self.setWindowIcon(QIcon(icon_path))
        self.db = Database()
        self.current_user = None
        self.init_ui()
        
    def check_auto_login(self):
        """Проверить, есть ли сохранённый пользователь"""
        saved_user = load_session()
        print(f"Загружен пользователь {saved_user}")
        if saved_user:
            # Проверяем, существует ли пользователь в БД
            success, result = self.db.auto_login(saved_user)
            print(f"Авто-вход: {success}, {result}")
            if success:
                self.current_user = saved_user
                self.auto_login_done = True
                self.opened = True
                self.open_game_menu()
                return True
        return False
            
    def open_game_menu(self):
        self.menu_window = GameMenuWindow(self.current_user)
        self.menu_window.show()
        self.hide()
                    
    def init_ui(self):
        self.setWindowTitle("ChessBox")
        self.setFixedSize(400, 400)
        
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout()
        central.setLayout(main_layout)
        
        # Заголовок
        title = QLabel("ChessBox")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 32px; font-weight: bold; margin: 20px;")
        main_layout.addWidget(title)
        
        # Вкладки
        self.tabs = QTabWidget()
        self.login_tab = QWidget()
        self.register_tab = QWidget()
        self.tabs.addTab(self.login_tab, "Вход")
        self.tabs.addTab(self.register_tab, "Регистрация")
        main_layout.addWidget(self.tabs)
        
        # === ВКЛАДКА ВХОДА ===
        login_layout = QVBoxLayout()
        
        self.login_username = QLineEdit()
        self.login_username.setPlaceholderText("Имя пользователя")
        login_layout.addWidget(self.login_username)
        
        self.login_password = QLineEdit()
        self.login_password.setPlaceholderText("Пароль")
        self.login_password.setEchoMode(QLineEdit.EchoMode.Password)
        login_layout.addWidget(self.login_password)
        
        login_btn = QPushButton("Войти")
        login_btn.clicked.connect(self.do_login)
        login_layout.addWidget(login_btn)
        
        login_layout.addStretch()
        self.login_tab.setLayout(login_layout)
        
        # === ВКЛАДКА РЕГИСТРАЦИИ ===
        register_layout = QVBoxLayout()
        
        self.reg_username = QLineEdit()
        self.reg_username.setPlaceholderText("Имя пользователя")
        register_layout.addWidget(self.reg_username)
        
        self.reg_password = QLineEdit()
        self.reg_password.setPlaceholderText("Пароль")
        self.reg_password.setEchoMode(QLineEdit.EchoMode.Password)
        register_layout.addWidget(self.reg_password)
        
        self.reg_confirm = QLineEdit()
        self.reg_confirm.setPlaceholderText("Подтвердите пароль")
        self.reg_confirm.setEchoMode(QLineEdit.EchoMode.Password)
        register_layout.addWidget(self.reg_confirm)
        
        register_btn = QPushButton("Зарегистрироваться")
        register_btn.clicked.connect(self.do_register)
        register_layout.addWidget(register_btn)
        
        register_layout.addStretch()
        self.register_tab.setLayout(register_layout)
        
        # Статус
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.status_label)
    
    def show_message(self, text, is_error=False):
        self.status_label.setText(text)
        if is_error:
            self.status_label.setStyleSheet("color: red;")
        else:
            self.status_label.setStyleSheet("color: green;")
    
    def do_login(self):
        username = self.login_username.text().strip()
        password = self.login_password.text()
        
        if not username or not password:
            self.show_message("Заполните все поля!", True)
            return
        
        success, result = self.db.login_user(username, password)
        if success:
            self.current_user = username
            # Сохраняем сессию на диск в папку Session
            save_session(username)
            print(f"[LoginWindow] Сессия сохранена для {username}")
            self.show_message(f"Добро пожаловать, {username}!")
            self.open_game_menu()
        else:
            self.show_message(result, True)
    
    def do_register(self):
        username = self.reg_username.text().strip()
        password = self.reg_password.text()
        confirm = self.reg_confirm.text()
        
        if not username or not password:
            self.show_message("Заполните все поля!", True)
            return
        
        if password != confirm:
            self.show_message("Пароли не совпадают!", True)
            return
        
        success, message = self.db.register_user(username, password)
        self.show_message(message, not success)
        
        if success:
            self.tabs.setCurrentIndex(0)
            self.login_username.setText(username)
            self.login_password.setText("")
    
                
class GameMenuWindow(QMainWindow):
    def __init__(self, username):
        super().__init__()
        # Устанавливаем иконку для окна
        icon_path = resource_path("icon.ico")
        self.setWindowIcon(QIcon(icon_path))
        self.username = username
        self.db = Database()
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("ChessBox")
        self.setFixedSize(500, 450)
        
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout()
        central.setLayout(layout)
        
        logout_btn = QPushButton("🚪 Выйти из аккаунта")
        logout_btn.clicked.connect(self.logout)
        layout.addWidget(logout_btn)
        logout_btn.setStyleSheet("""
    QPushButton {background-color: #f0f0f0; border: 2px solid #dcdcdc;
    border-radius: 12px; color: #333; padding: 8px 16px; font-size: 14px; font-weight: 650;
    }
    QPushButton:hover {background-color: #e5e5e5; border-color: #bbb;}
    QPushButton:pressed { background-color: #d0d0d0;}
    """)
        layout.addSpacing(20)
        # Приветствие
        welcome = QLabel(f"Добро пожаловать, {self.username}!")
        welcome.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome.setStyleSheet("font-size: 23px; font-weight: 700;; margin: 20px;")
        layout.addWidget(welcome)
        layout.addSpacing(20)
        
        # Кнопки режимов
        
        offline_btn = QPushButton("🎮 Играть offline")
        layout.addWidget(offline_btn)
        offline_btn.clicked.connect(self.open_gamemode_choice_window)
        offline_btn.setStyleSheet("""
    QPushButton {background-color: #f0f0f0; border: 2px solid #dcdcdc;
    border-radius: 12px; color: #333; padding: 16.5px; font-size: 14px; font-weight: 650;
    }
    QPushButton:hover {background-color: #e5e5e5; border-color: #bbb;}
    QPushButton:pressed { background-color: #d0d0d0;}
    """)
        online_btn = QPushButton("🌐 Играть online")
        layout.addWidget(online_btn)
        online_btn.clicked.connect(self.start_network_setup)
        online_btn.setStyleSheet("""
    QPushButton {background-color: #f0f0f0; border: 2px solid #dcdcdc;
    border-radius: 12px; color: #333; padding: 16.5px; font-size: 14px; font-weight: 650;
    }
    QPushButton:hover {background-color: #e5e5e5; border-color: #bbb;}
    QPushButton:pressed { background-color: #d0d0d0;}
    """)
        self.sandbox_btn = QPushButton("🏖️ Играть в песочницу (в разработке)")
        layout.addWidget(self.sandbox_btn)
        self.sandbox_btn.clicked.connect(self.start_sandbox_mode)
        self.sandbox_btn.setStyleSheet("""
    QPushButton {background-color: #f0f0f0; border: 2px solid #dcdcdc;
    border-radius: 12px; color: #333; padding: 16.5px; font-size: 14px; font-weight: 650;
    }
    QPushButton:hover {background-color: #e5e5e5; border-color: #bbb;}
    QPushButton:pressed { background-color: #d0d0d0;}
    """)
        self.stats_btn = QPushButton("📊 Статистика")
        layout.addWidget(self.stats_btn)
        self.stats_btn.clicked.connect(self.show_stats)
        self.stats_btn.setStyleSheet("""
    QPushButton {background-color: #f0f0f0; border: 2px solid #dcdcdc;
    border-radius: 12px; color: #333; padding: 16.5px; font-size: 14px; font-weight: 650;
    }
    QPushButton:hover {background-color: #e5e5e5; border-color: #bbb;}
    QPushButton:pressed { background-color: #d0d0d0;}
    """)
        layout.addStretch()
        
    def start_sandbox_mode(self):
        self.sandbox_btn.setText("Песочница в разработке!")   
        
    def open_gamemode_choice_window(self):
        self.game_mode_window = Gamemode_Window(self.username)
        self.game_mode_window.show()
        self.close()
        
    def show_stats(self):
        self.stats_window = Stats_window(self.username)
        self.stats_window.show()
        self.close()
        
    def logout(self):
        """Выйти из аккаунта"""
        clear_session()  # удаляем сохранённого пользователя
        self.close()
        # Возвращаемся в окно входа
        self.login_window = LoginWindow()
        self.login_window.show()

    def start_game(self, gamemode=None):
        self.game_window = ChessWindow(game=None, gamemode = gamemode, username=self.username)
        self.game_window.show()
        self.close()
        
    def closeEvent(self, event):
        #типо alt + f4 или крестик
        event.accept()  # закрываем окно, сессия остаётся
        
    def start_network_setup(self):
        """Открыть окно настройки сетевой игры"""
        self.network_window = NetworkSetupWindow(self.username)
        self.network_window.show()
        self.close()

class NetworkSetupWindow(QMainWindow):
    """Окно настройки сетевой игры"""
    
    def __init__(self, username):
        super().__init__()
        # Устанавливаем иконку для окна
        icon_path = resource_path("icon.ico")
        self.setWindowIcon(QIcon(icon_path))
        self.username = username
        self.network = P2PNetwork()
        self.network.move_received.connect(self.on_network_move)
        self.network.opponent_connected.connect(self.on_opponent_connected)
        self.network.opponent_disconnected.connect(self.on_opponent_disconnected)
        self.network.status_message.connect(self.update_network_status)
        self.network.gamemode_received.connect(self.on_gamemode_received)
        self.init_ui()
    
    def on_gamemode_received(self,gamemode):
        self.start_network_game(gamemode)
        
    def init_ui(self):
        self.setWindowTitle("ChessBox")
        self.setFixedSize(500, 340)
        
        layout = QVBoxLayout()
        central = QWidget()
        central.setLayout(layout)
        self.setCentralWidget(central)
        
        # Заголовок
        title = QLabel("🌐 Сетевая игра")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)
        
        # Статус сети
        self.network_status = QLabel("Офлайн")
        self.network_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.network_status.setStyleSheet("color: gray; font-weight: bold;")
        layout.addWidget(self.network_status)
        
        # IP
        self.ip_label = QLabel(f"Ваш IP: {self.network.get_local_ip()}")
        self.ip_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.ip_label)
        self.ip_label.setStyleSheet("color: black; font-size: 15px; font-weight: 650;")
        layout.addSpacing(13)
        
        # Кнопки
        self.host_btn = QPushButton("🎮 Создать игру (сервер)")
        self.host_btn.clicked.connect(self.host_game)
        layout.addWidget(self.host_btn)
        self.host_btn.setStyleSheet("""
    QPushButton {background-color: #f0f0f0; border: 2px solid #dcdcdc;
    border-radius: 12px; color: #333; padding: 10px; font-size: 16px; font-weight: 650;
    }
    QPushButton:hover {background-color: #e5e5e5; border-color: #bbb;}
    QPushButton:pressed { background-color: #d0d0d0;}
    """)
        
        
        self.join_btn = QPushButton("🔌 Подключиться к игре")
        self.join_btn.clicked.connect(self.join_game)
        layout.addWidget(self.join_btn)
        self.join_btn.setStyleSheet("""
    QPushButton {background-color: #f0f0f0; border: 2px solid #dcdcdc;
    border-radius: 12px; color: #333; padding: 10px; font-size: 16px; font-weight: 650;
    }
    QPushButton:hover {background-color: #e5e5e5; border-color: #bbb;}
    QPushButton:pressed { background-color: #d0d0d0;}
    """)
        
        self.disconnect_btn = QPushButton("❌ Отключиться")
        self.disconnect_btn.clicked.connect(self.disconnect)
        self.disconnect_btn.setEnabled(False)
        layout.addWidget(self.disconnect_btn)
        self.disconnect_btn.setStyleSheet("""
    QPushButton {background-color: #f0f0f0; border: 2px solid #dcdcdc;
    border-radius: 12px; color: #333; padding: 10px; font-size: 16px; font-weight: 650;
    }
    QPushButton:hover {background-color: #e5e5e5; border-color: #bbb;}
    QPushButton:pressed { background-color: #d0d0d0;}
    """)
        
        # Кнопка назад
        back_btn = QPushButton("← Назад")
        back_btn.clicked.connect(self.go_back)
        layout.addWidget(back_btn)
        back_btn.setStyleSheet("""
    QPushButton {background-color: #f0f0f0; border: 2px solid #dcdcdc;
    border-radius: 12px; color: #333; padding: 10px; font-size: 16px; font-weight: 650;
    }
    QPushButton:hover {background-color: #e5e5e5; border-color: #bbb;}
    QPushButton:pressed { background-color: #d0d0d0;}
    """)
        
        layout.addStretch()
    
    def host_game(self):
        if self.network.host_game(5555):
            self.host_btn.setEnabled(False)
            self.join_btn.setEnabled(False)
            self.disconnect_btn.setEnabled(True)
            self.update_network_status("Ожидание игрока...")
    
    def join_game(self):
        ip, ok = QInputDialog.getText(
            self, 
            "Подключение", 
            "Введите IP противника:",
            text=self.network.get_local_ip()
        )
        if ok and ip:
            if self.network.join_game(ip, 5555):
                self.host_btn.setEnabled(False)
                self.join_btn.setEnabled(False)
                self.disconnect_btn.setEnabled(True)
    
    def disconnect(self):
        self.network.disconnect()
        self.host_btn.setEnabled(True)
        self.join_btn.setEnabled(True)
        self.disconnect_btn.setEnabled(False)
        self.update_network_status("Отключён")
    
    def update_network_status(self, message):
        self.network_status.setText(message)
        if "ошибка" in message.lower():
            self.network_status.setStyleSheet("color: red; font-weight: bold;")
        elif "подключ" in message.lower() or "игрок" in message.lower():
            self.network_status.setStyleSheet("color: green; font-weight: bold;")
        else:
            self.network_status.setStyleSheet("color: blue; font-weight: bold;")
            
    def on_opponent_connected(self):
        self.update_network_status("Противник подключился!")
        if self.network.is_host:
            QMessageBox.information(self, "Сеть", "Противник подключён!")
            self.open_gamemode_choice_window()
        else:
            QMessageBox.information(self, "Сеть", "Противник подключён!\nОжидаем выбора режима игры.")
    
    def on_opponent_disconnected(self):
        # если флаг is_exiting существует и он True - мы сами выходим, молчим
        if self.network.is_exiting == True:
             # сбросим для будущих игр
            self.disconnect()
        # иначе противник отключился по настоящему
        else:
            self.update_network_status("Противник отключился")
            QMessageBox.warning(self, "Сеть", "Противник отключился.")
            self.disconnect()
    
    def on_network_move(self, from_pos, to_pos):
        """Получен ход от противника (передаётся в игровое окно)"""
        if hasattr(self, 'game_window') and self.game_window:
            self.game_window.on_network_move(from_pos, to_pos)
    
    def start_network_game(self, gamemode):
         """Запустить игру с сетью"""
         self.game_window = ChessWindow(
            game=None, 
            gamemode=gamemode, 
            username=self.username,
            network=self.network  # передаём сеть
        )
         self.game_window.show()
         self.close()
        
    def open_gamemode_choice_window(self):
        self.game_mode_window = Gamemode_Window(self.username, self.network)
        self.game_mode_window.show()
        self.close()
        
    def go_back(self):
        """Вернуться в главное меню"""
        if self.network:
            self.network.disconnect()
        self.close()
        self.menu_window = GameMenuWindow(self.username)
        self.menu_window.show()
        
class Gamemode_Window(QMainWindow):
    def __init__(self,username,network=None):
        self.network = network
        super().__init__()
        # Устанавливаем иконку для окна
        icon_path = resource_path("icon.ico")
        self.setWindowIcon(QIcon(icon_path))
        self.username = username
        self.setWindowTitle("ChessBox - выбор режима")
        self.setFixedSize(500, 370)

        title = QLabel("<b>⬇ Выберите режим игры</b>")
        title.setStyleSheet("font-size: 24px; color: black;")

        self.bullet_button = QPushButton("🔫 Bullet (1.5 минуты)")
        self.blitz_button = QPushButton("⚡ Blitz (5 минут)")
        self.rapid_button = QPushButton(" ⏱️ Rapid (15 минут) ")
        self.endless_button = QPushButton(" ∞ Endless (неограниченно) ")
        self.back_button = QPushButton("← Назад")
        
        self.bullet_button.clicked.connect(self.bullet_timer)
        self.blitz_button.clicked.connect(self.blitz_timer)
        self.rapid_button.clicked.connect(self.rapid_timer)
        self.endless_button.clicked.connect(self.endless_timer)
        self.back_button.clicked.connect(self.go_back)
        
        layout = QVBoxLayout()
        layout.addStretch(1)
        layout.addWidget(title)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addSpacing(25)
        layout.addWidget(self.bullet_button)
        layout.addWidget(self.blitz_button)
        layout.addWidget(self.rapid_button)
        layout.addWidget(self.endless_button)
        layout.addWidget(self.back_button)
        layout.addSpacing(20)
        layout.setContentsMargins(10,0,10,0) 
        
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        
        self.bullet_button.setStyleSheet("""
    QPushButton {background-color: #f0f0f0; border: 2px solid #dcdcdc;
    border-radius: 12px; color: #333; padding: 10px; font-size: 16px; font-weight: 650;
    }
    QPushButton:hover {background-color: #e5e5e5; border-color: #bbb;}
    QPushButton:pressed { background-color: #d0d0d0;}
    """)
        
        self.blitz_button.setStyleSheet("""
    QPushButton {background-color: #f0f0f0; border: 2px solid #dcdcdc;
    border-radius: 12px; color: #333; padding: 10px; font-size: 16px; font-weight: 650;
    }
    QPushButton:hover {background-color: #e5e5e5; border-color: #bbb;}
    QPushButton:pressed { background-color: #d0d0d0;}
    """)
        
        self.rapid_button.setStyleSheet("""
    QPushButton {background-color: #f0f0f0; border: 2px solid #dcdcdc;
    border-radius: 12px; color: #333; padding: 10px; font-size: 16px; font-weight: 650;
    }
    QPushButton:hover {background-color: #e5e5e5; border-color: #bbb;}
    QPushButton:pressed { background-color: #d0d0d0;}
    """)
        
        self.endless_button.setStyleSheet("""
    QPushButton {background-color: #f0f0f0; border: 2px solid #dcdcdc;
    border-radius: 12px; color: #333; padding: 10px; font-size: 16px; font-weight: 650;
    }
    QPushButton:hover {background-color: #e5e5e5; border-color: #bbb;}
    QPushButton:pressed { background-color: #d0d0d0;}
    """)
        self.back_button.setStyleSheet("""
    QPushButton {background-color: #f0f0f0; border: 2px solid #dcdcdc;
    border-radius: 12px; color: #333; padding: 10px; font-size: 16px; font-weight: 650;
    }
    QPushButton:hover {background-color: #e5e5e5; border-color: #bbb;}
    QPushButton:pressed { background-color: #d0d0d0;}
    """)
        
        title.setStyleSheet("""
    QLabel {
        color: black;
        border-radius: 10px;
        padding: 10px;
        font-size: 20px;
        font-weight: 600;
    }
""")
    def start_network_game(self, gamemode=None):
        """Запустить игру с сетью"""
        self.game_window = ChessWindow(game=None,  gamemode=gamemode, username=self.username, network=self.network
        )
        self.game_window.show()
        self.close()
                
    def bullet_timer(self):
        if self.network:
            self.network.send_gamemode("bullet")
            self.start_network_game("bullet")
        else:
            self.start_game("bullet")

    def blitz_timer(self):
        if self.network:
            self.network.send_gamemode("blitz")
            self.start_network_game("blitz")
        else:
            self.start_game("blitz")

    def rapid_timer(self):
        if self.network:
            self.network.send_gamemode("rapid")
            self.start_network_game("rapid")
        else:
            self.start_game("rapid")
        
    def endless_timer(self):
        if self.network:
            self.network.send_gamemode("endless")
            self.start_network_game("endless")
        else:
            self.start_game("endless")
    
    def start_game(self, gamemode=None):
        self.game_window = ChessWindow(game=None, gamemode = gamemode, username=self.username)
        self.game_window.show()
        self.close()
        
    def go_back(self):
        """Вернуться в главное меню"""
        self.close()
        self.menu_window = GameMenuWindow(self.username)
        self.menu_window.show()
        
class Stats_window(QMainWindow):
    def __init__(self, username):
        super().__init__()
        # Устанавливаем иконку для окна
        icon_path = resource_path("icon.ico")
        self.setWindowIcon(QIcon(icon_path))
        self.setWindowTitle("ChessBox")
        self.setFixedSize(500, 370)
        self.username = username
        self.db = Database()

        title = QLabel("<b>📊 Статистика</b>")
        title.setStyleSheet("font-size: 24px; color: black;")
        self.stats_label = QLabel()
        self.load_stats()
        self.back_button = QPushButton("← Назад")
        self.back_button.clicked.connect(self.go_back)
        
        layout = QVBoxLayout()
        layout.addStretch(1)
        layout.addWidget(title)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.stats_label)
        layout.addWidget(self.back_button)
        layout.addSpacing(5)
        layout.setContentsMargins(10,0,10,0) 
        
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        self.stats_label.setStyleSheet("color: black; font-size: 15px; font-weight: 600")
        self.back_button.setStyleSheet("""
    QPushButton {background-color: #f0f0f0; border: 2px solid #dcdcdc;
    border-radius: 12px; color: #333; padding: 10px; font-size: 16px; font-weight: 700;
    }
    QPushButton:hover {background-color: #e5e5e5; border-color: #bbb;}
    QPushButton:pressed { background-color: #d0d0d0;}
    """)
        
        title.setStyleSheet("""
    QLabel {
        color: black;
        border-radius: 10px;
        padding: 10px;
        font-size: 20px;
        font-weight: 600;
    }
""")
    def load_stats(self):
        stats = self.db.get_stats(self.username)
        
        if stats:
            bullet_wins = stats['bullet_wins']    
            bullet_losses = stats['bullet_losses']
            bullet_draws = stats['bullet_draws']
            blitz_wins = stats['blitz_wins']    
            blitz_losses = stats['blitz_losses']
            blitz_draws = stats['blitz_draws']
            rapid_wins = stats['rapid_wins']    
            rapid_losses = stats['rapid_losses']
            rapid_draws = stats['rapid_draws']
            endless_wins = stats['endless_wins']    
            endless_losses = stats['endless_losses']
            endless_draws = stats['endless_draws']
            total_wins = bullet_wins + blitz_wins + rapid_wins + endless_wins
            total_losses = bullet_losses + blitz_losses + rapid_losses + endless_losses
            total_draws = bullet_draws + blitz_draws + rapid_draws + endless_draws
            self.stats_label.setText(
                f"""
                Bullet: побед - {bullet_wins}, поражений - {bullet_losses}, ничьих - {bullet_draws}\n
                Blitz: побед - {blitz_wins}, поражений - {blitz_losses}, ничьих - {blitz_draws}\n
                Rapid: побед - {rapid_wins}, поражений - {rapid_losses}, ничьих - {rapid_draws}\n
                Timeless: Побед - {endless_wins}, поражений - {endless_losses}, ничьих - {endless_draws}\n
                Всего: побед - {total_wins}, поражений - {total_losses}, ничьих - {total_draws}
                
                """
            )
    def go_back(self):
        """Вернуться в главное меню"""
        self.close()
        self.menu_window = GameMenuWindow(self.username)
        self.menu_window.show()    