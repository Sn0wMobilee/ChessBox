from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from Engine.game import Game
from Network.network import P2PNetwork 
from Engine.pieces import Queen, Rook, Bishop, Knight, Pawn
import os
import sys
from DataBase.database import Database
from Engine.utils import resource_path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class ChessSquare(QLabel):
    """ШАХМАТНАЯ КЛЕТКА"""
    def __init__(self, row, col):
        super().__init__()
        self.row = row
        self.col = col
        self.is_light = (row + col) % 2 == 0 #светлые клетки - черные
        
        self.setAlignment(Qt.AlignmentFlag.AlignCenter) #выравнивание по центру
        self.setFixedSize(60, 60)#размер 60 на 60 пикселей
        self.setScaledContents(True) #для картинок
        self.update_style() #ну и покраска клеток
    
    def update_style(self):
        """КРАСКА КЛЕТОК"""
        if self.is_light:
            self.setStyleSheet("background-color: #f0d9b5; border: 1px solid #8b4513;") #свеьдый
        else:
            self.setStyleSheet("background-color: #b58863; border: 1px solid #8b4513;") #черный
            

class GameResultDialog(QDialog):
    def __init__(self, parent, result_text, network, gamemode, username):
        super().__init__(parent)
        # Устанавливаем иконку для окна
        icon_path = resource_path("icon.ico")
        self.setWindowIcon(QIcon(icon_path))
        
        self.parent = parent
        self.network = network
        self.gamemode = gamemode
        self.username = username
        self.setWindowTitle("ChessBox - результат игры")
        self.setFixedSize(300, 200)
        self.setModal(True)  # блокирует основное окно
        self.network.rematch_request_received.connect(self.on_rematch_request)
        self.network.rematch_accept_received.connect(self.on_rematch_accept)
        self.network.rematch_decline_received.connect(self.on_rematch_decline)

        layout = QVBoxLayout()
        self.setLayout(layout)  # для QDialog используется setLayout, но можно и так
        
        # Заголовок
        title = QLabel("🏆 ИГРА ОКОНЧЕНА 🏆")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)
        
        # Результат
        result_label = QLabel(result_text)
        result_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        result_label.setStyleSheet("font-size: 14px; margin: 10px;")
        layout.addWidget(result_label)
        
        # Кнопки
        buttons_layout = QHBoxLayout()
        
        self.rematch_btn = QPushButton("🔁 Реванш")
        self.rematch_btn.clicked.connect(self.on_rematch)
        buttons_layout.addWidget(self.rematch_btn)
        self.rematch_btn.setStyleSheet("""
    QPushButton {background-color: #f0f0f0; border: 2px solid #dcdcdc;
    border-radius: 12px; color: #333; padding: 10px; font-size: 16px; font-weight: 650;
    }
    QPushButton:hover {background-color: #e5e5e5; border-color: #bbb;}
    QPushButton:pressed { background-color: #d0d0d0;}
    """)
        
        self.exit_btn = QPushButton("🏠 Выйти в меню")
        self.exit_btn.clicked.connect(self.on_exit)
        buttons_layout.addWidget(self.exit_btn)
        self.exit_btn.setStyleSheet("""
    QPushButton {background-color: #f0f0f0; border: 2px solid #dcdcdc;
    border-radius: 12px; color: #333; padding: 10px; font-size: 16px; font-weight: 650;
    }
    QPushButton:hover {background-color: #e5e5e5; border-color: #bbb;}
    QPushButton:pressed { background-color: #d0d0d0;}
    """)
        
        layout.addLayout(buttons_layout)
        self.setLayout(layout)
        self.waiting_dialog = None
        
    def on_rematch(self):
        self.network.send_rematch_request()
        self.waiting_dialog = QMessageBox(self)
        self.waiting_dialog.setWindowTitle("Ожидание")
        self.waiting_dialog.setText("Ожидаем согласия соперника...")
        self.waiting_dialog.setStandardButtons(QMessageBox.StandardButton.NoButton)
        self.waiting_dialog.show()

    def on_rematch_request(self):     
        reply = QMessageBox.question(
            self,
            "Запрос на реванш",
            "Соперник хочет сыграть ещё раз. Принять?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            print("Отправляем rematch_accept")
            self.network.send_rematch_accept()
            self.close()
            self.parent.reset_game()
        else:
            self.network.send_rematch_decline()
            self.close()
            self.parent.exit_to_menu()
    
    def on_rematch_accept(self):
        print("Сбрасываем игру")
        if self.waiting_dialog:
            self.waiting_dialog.close()
        self.close()
        self.parent.reset_game()

    def on_rematch_decline(self):
        QMessageBox.information(self, "Реванш отклонён", "Соперник отказался от реванша.")
        if self.waiting_dialog:
            self.waiting_dialog.close()
        self.close()
        self.parent.exit_to_menu()

    def on_exit(self):
        if self.waiting_dialog:
            self.waiting_dialog.close()
        self.close()
        self.parent.exit_to_menu()
        
        
class PromotionDialog(QDialog):
    def __init__(self, parent, color):
        super().__init__(parent)
        self.color = color
        self.setWindowTitle("Превращение пешки")
        self.setModal(True)
        self.setFixedSize(300, 120)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.CustomizeWindowHint)
        
        layout = QVBoxLayout()
        title = QLabel("             Выберите фигуру:")
        layout.addWidget(title)
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        
        buttons_layout = QHBoxLayout()
        
        pieces = ["queen", "rook", "bishop", "knight"]
        self.selected_piece = None
        
        for piece_type in pieces:
            filename = f"assets/{color}_{piece_type}.png"
            
            if os.path.exists(filename):
                pixmap = QPixmap(filename)
                if not pixmap.isNull():
                    scaled = pixmap.scaled(40, 40, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                    btn = QPushButton()
                    btn.setIcon(QIcon(scaled))
                    btn.setIconSize(scaled.size())
                    btn.setFixedSize(50, 50)
                    btn.clicked.connect(lambda checked, pt=piece_type: self.select_piece(pt))
                    buttons_layout.addWidget(btn)
                    continue
            
            # fallback на символы
            symbol_map = {
                'queen': '♕' if color == 'white' else '♛',
                'rook': '♖' if color == 'white' else '♜',
                'bishop': '♗' if color == 'white' else '♝',
                'knight': '♘' if color == 'white' else '♞'
            }
            btn = QPushButton(symbol_map[piece_type])
            btn.setFixedSize(50, 50)
            btn.setFont(QFont("Segoe UI", 20))
            btn.clicked.connect(lambda checked, pt=piece_type: self.select_piece(pt))
            buttons_layout.addWidget(btn)
        
        layout.addLayout(buttons_layout)
        self.setLayout(layout)
        
    def closeEvent(self, event):
        event.ignore()
        
    def select_piece(self, piece_type):
        self.selected_piece = piece_type
        self.accept()
        
                
class ChessWindow(QMainWindow):
    """ГЛАВНОЕ ОКНО"""
    def __init__(self, game=None, gamemode=None, username=None, network=None):
        super().__init__()
        icon_path = resource_path("icon.ico")
        self.setWindowIcon(QIcon(icon_path))
        self.game_over = False # флаг, закончена ли игра?
        self.username = username  # сохраняем имя для статистики
        self.gamemode = gamemode  # сохраняем режим игры
        self.db = Database() #база данных для статистики
        self.network = network #ну и сеть
        #ЗАГРУЗКА ИГРЫ
        if game:
            self.game = game #если есть игра то открыть ее
        else:
            from Engine.game import Game 
            self.game = Game() #если нет то создать
        self.white_seconds_left = None
        self.black_seconds_left = None
        
        if self.gamemode == "bullet":
            self.white_seconds_left = 900
            self.black_seconds_left = 900
        elif self.gamemode == "blitz":
            self.white_seconds_left = 3000
            self.black_seconds_left = 3000
        elif self.gamemode == "rapid":
            self.white_seconds_left = 9000
            self.black_seconds_left = 9000
        elif self.gamemode == "endless":
            self.white_seconds_left = None
            self.black_seconds_left = None
            
        #СЕТЕВЫЕ МОДУЛИ
        if self.network: #если игра сетевая:
            self.network.move_received.connect(self.on_network_move) #получение хода от противника
            self.network.opponent_connected.connect(self.on_opponent_connected) #противник подключился
            self.network.opponent_disconnected.connect(self.on_opponent_disconnected) #противник отключился
            self.network.status_message.connect(self.update_network_status) #обновление статуса сети (ошибка подключения, противник подключился и др.)
            self.network.resign_received.connect(self.on_opponent_resign) #противник сдался
        
        #КЛЕТКИ НЕ ВЫБРАНЫ
        self.selected_square = None
        
        #ЗАПУСК ПРОГИ
        self.init_ui()
        self.update_board()

    def init_ui(self):
        """САМ ГРАФИЧЕСКИЙ ИНТЕРФЕЙС"""
        self.setWindowTitle("ChessBox")
        self.setFixedSize(650, 650)
        
        central = QWidget()
        self.setCentralWidget(central)
        
        # ГЛАВНЫЙ ВЕРТИКАЛЬНЫЙ LAYOUT
        main_layout = QVBoxLayout()
        central.setLayout(main_layout)
        
                # Таймеры
        
        #  ВЕРХНЯЯ ПАНЕЛЬ 
        top_panel = QHBoxLayout()
        top_panel.setContentsMargins(0, 0, 0, 0)

        # Растяжка слева
        top_panel.addStretch()

        # Чёрный таймер (по центру)
        self.black_timer = QLabel("15:00")
        self.black_timer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.black_timer.setFixedWidth(130)
        self.black_timer.setFixedHeight(43)
        self.black_timer.setStyleSheet("""
            QLabel {
                background-color: #2c2c2c;
                color: #ffffff;
                border-radius: 8px;
                padding: 6px;
                font-family: 'Consolas', monospace;
                font-size: 16px;
                font-weight: bold;
                border: 2px solid #555;
            }
        """)
        top_panel.addWidget(self.black_timer)

        # Отступ между таймером и статусом
        top_panel.addSpacing(30)

        # Статус сети (справа от чёрного таймера)
        if self.network:
            self.network_status = QLabel("🌐 Подключено")
            self.network_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.network_status.setFixedWidth(130)
            self.network_status.setFixedHeight(43)
            self.network_status.setStyleSheet("""
            QLabel {
                background-color: #f0f0f0;
                color: #000000;
                border-radius: 8px;
                padding: 6px;
                font-family: 'Consolas', monospace;
                font-size: 14px;
                font-weight: bold;
                border: 2px solid #aaa;
            }
        """)
            top_panel.addWidget(self.network_status)
        else:
            self.network_status = QLabel("Офлайн")
            self.network_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.network_status.setFixedWidth(130)
            self.network_status.setFixedHeight(43)
            self.network_status.setStyleSheet("""
            QLabel {
                background-color: #f0f0f0;
                color: #000000;
                border-radius: 8px;
                padding: 6px;
                font-family: 'Consolas', monospace;
                font-size: 14px;
                font-weight: bold;
                border: 2px solid #aaa;
            }
        """)
            top_panel.addWidget(self.network_status)
            
        # Растяжка справа
        top_panel.addStretch()

        main_layout.addLayout(top_panel)
        
        #  ДОСКА 
        board_widget = QWidget()
        board_widget.setFixedSize(480, 480)
        board_layout = QGridLayout()
        board_layout.setSpacing(0)
        board_widget.setLayout(board_layout)
        
        self.squares = []
        for row in range(8):
            row_squares = []
            for col in range(8):
                square = ChessSquare(row, col)
                square.mousePressEvent = lambda _, r=row, c=col: self.on_square_click(r, c)
                row_squares.append(square)
                board_layout.addWidget(square, row, col)
            self.squares.append(row_squares)
        
        main_layout.addWidget(board_widget, alignment=Qt.AlignmentFlag.AlignCenter)
        
            #НИЖНЯЯ ПАНЕЛЬ
        bottom_panel = QHBoxLayout()
        bottom_panel.setContentsMargins(0, 10, 0, 10)

        # Растяжка слева, чтобы белый таймер был по центру
        bottom_panel.addStretch()

        # Белый таймер 
        self.white_timer = QLabel("15:00")
        self.white_timer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.white_timer.setFixedWidth(130)
        self.white_timer.setFixedHeight(43)
        self.white_timer.setStyleSheet("""
            QLabel {
                background-color: #f0f0f0;
                color: #000000;
                border-radius: 8px;
                padding: 6px;
                font-family: 'Consolas', monospace;
                font-size: 16px;
                font-weight: bold;
                border: 2px solid #aaa;
            }
        """)
        bottom_panel.addWidget(self.white_timer)

        # Отступ между таймером и кнопкой
        bottom_panel.addSpacing(30)

        # Кнопка выхода/сдачи (справа от белого таймера)
        if not self.network:
            # Оффлайн: кнопка выхода в меню
            self.menu_btn = QPushButton("🏠 Выйти в меню")
            self.menu_btn.setFixedWidth(130)
            self.menu_btn.setFixedHeight(43)
            self.menu_btn.setStyleSheet("""
                QPushButton {
                    background-color: #ffc107;
                    border-radius: 8px;
                    padding: 6px;
                    color: #333;
                    font-size: 13px;
                    font-weight: bold;
                    border: 2px solid #aaa;
                }
                QPushButton:hover { background-color: #e0a800; }
                QPushButton:pressed { background-color: #c69500; }
            """)
            self.menu_btn.clicked.connect(self.exit_to_menu)
            bottom_panel.addWidget(self.menu_btn)

        if self.network:
            # Онлайн: кнопка сдачи
            self.resign_btn = QPushButton("🏳️ Сдаться")
            self.resign_btn.setFixedWidth(130)
            self.resign_btn.setFixedHeight(43)
            self.resign_btn.setStyleSheet("""
                QPushButton {
                    background-color: #dc3545;
                    border-radius: 8px;
                    padding: 6px;
                    color: white;
                    font-size: 13px;
                    font-weight: bold;
                    border: 2px solid #aaa;
                }
                QPushButton:hover { background-color: #c82333; }
                QPushButton:pressed { background-color: #a71d2a; }
            """)
            self.resign_btn.clicked.connect(self.resign_game)
            bottom_panel.addWidget(self.resign_btn)

        # Растяжка справа для баланса
        bottom_panel.addStretch()
        main_layout.addLayout(bottom_panel)
        
        self.timer_engine_white = QTimer()
        self.timer_engine_black = QTimer()
        self.timer_engine_white.timeout.connect(self.on_white_timer)
        self.timer_engine_black.timeout.connect(self.on_black_timer)
        
        self.define_timerstate()
        
    def reset_game(self):
        """Полный сброс игры для реванша"""
        self.game = Game()
        self.game_over = False
        self.selected_square = None
        # Сброс времени
        self.white_seconds_left = None
        self.black_seconds_left = None
        if self.gamemode == "bullet":
            self.white_seconds_left = 900
            self.black_seconds_left = 900
        elif self.gamemode == "blitz":
            self.white_seconds_left = 3000
            self.black_seconds_left = 3000
        elif self.gamemode == "rapid":
            self.white_seconds_left = 9000
            self.black_seconds_left = 9000
        elif self.gamemode == "endless":
            self.white_seconds_left = None
            self.black_seconds_left = None
        
        self.timer_engine_white.stop()
        self.timer_engine_black.stop()
        self.update_timerstate()
        self.update_board()
        self.update_turn_status()  
          
    def _stop_game_completely(self):
        if hasattr(self, 'timer_engine_white'):
            self.timer_engine_white.stop()
        if hasattr(self, 'timer_engine_black'):
            self.timer_engine_black.stop()
        if self.network:
            self.network.disconnect()
            
    def closeEvent(self, event):
        if self.network:
            self.network.is_exiting = True
        self._stop_game_completely()
        event.accept()
                 
    def define_timerstate(self):
        if self.game.board.white_player_has_moved == False:
            self.timer_engine_white.stop()
            self.timer_engine_black.stop()
        else:
            self.update_timer()
        if self.gamemode == "bullet":
            self.white_timer.setText("1:30")
            self.black_timer.setText("1:30")
        elif self.gamemode == "blitz":
            self.white_timer.setText("5:00")
            self.black_timer.setText("5:00")
        elif self.gamemode == "rapid":
            self.white_timer.setText("15:00")
            self.black_timer.setText("15:00")
        elif self.gamemode == "endless":
            self.white_timer.setText("Nothing")
            self.black_timer.setText("Nothing")
            self.white_timer.hide()
            self.black_timer.hide()
            
    def update_timerstate(self):
        if self.gamemode == "bullet":
            self.white_timer.setText("1:30")
            self.black_timer.setText("1:30")
        elif self.gamemode == "blitz":
            self.white_timer.setText("5:00")
            self.black_timer.setText("5:00")
        elif self.gamemode == "rapid":
            self.white_timer.setText("15:00")
            self.black_timer.setText("15:00")
        elif self.gamemode == "endless":
            self.white_timer.setText("Nothing")
            self.black_timer.setText("Nothing")
            self.white_timer.hide()
            self.black_timer.hide()
        if self.game.board.white_player_has_moved == False:
            self.timer_engine_white.stop()
            self.timer_engine_black.stop()
        else:
            self.update_timer()    
                  
    def on_white_timer(self):
        if self.white_seconds_left is None:
            pass
        elif self.white_seconds_left > 0:
            self.white_seconds_left -= 1
            time_obj = QTime(0, 0, 0).addMSecs(self.white_seconds_left * 100)
            self.white_timer.setText(time_obj.toString("mm:ss"))
        elif self.white_seconds_left == 0:
            self.timer_engine_white.stop()
            self._handle_time_loss("white")
        
    def on_black_timer(self):
        if self.black_seconds_left is None:
            pass
        elif self.black_seconds_left > 0:
            self.black_seconds_left -= 1
            time_obj = QTime(0, 0, 0).addMSecs(self.black_seconds_left * 100)
            self.black_timer.setText(time_obj.toString("mm:ss"))
        elif self.black_seconds_left == 0:
            self.timer_engine_black.stop()
            self._handle_time_loss("black")
        
    def _handle_time_loss(self, loser_color):
        """Обработка поражения по времени (общий код для белых и чёрных)"""
        self.game_over = True
        self.stop_timers() 
        if hasattr(self, 'network') and self.network and self.network.is_connected():
            # СЕТЕВАЯ ИГРА
            self.update_stats_after_game('loss', self.gamemode)
            winner = "чёрные" if loser_color == "white" else "белые"
            text = f"Время вышло!\n{'Белые' if loser_color == 'white' else 'Чёрные'} проиграли по времени!\nПобедили {winner}!"
            self.show_game_result_dialog(text)
        else:
            winner = "Чёрные" if loser_color == "white" else "Белые"
            text = f"Время вышло!\n{'Белые' if loser_color == 'white' else 'Чёрные'} проиграли по времени!\nПобедили {winner}!"
            QMessageBox.information(self,"Время вышло!",text, QMessageBox.StandardButton.Ok)
            self.offer_rematch()
        
    def show_game_result_dialog(self, result_text):
            dialog = GameResultDialog(self,result_text, self.network, self.gamemode,self.username)
            dialog.exec()
         
    def exit_to_menu(self):
        """Выйти в главное меню с предупреждением"""
        if self.game_over == False:
            reply = QMessageBox.question(
                self,
                "Выход в меню",
                "Вы уверены, что хотите выйти?\nТекущая игра будет потеряна.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            ) #чисто кнопка с выбором
            
            if reply == QMessageBox.StandardButton.Yes:
                #если есть сеть - отключаемся
                if self.network:
                    self.network.is_exiting = True
                    self.network.disconnect()
                self._stop_game_completely()
                self.close()
                
                #открываем главное меню
                from Gui.main_menu import GameMenuWindow
                self.menu_window = GameMenuWindow(self.username)
                self.menu_window.show()
        #если окончена то без предупреждения
        elif self.game_over == True:
            if self.network:
                self.network.is_exiting = True
                self.network.disconnect()
            self._stop_game_completely()
            self.close()
                #открываем главное меню
            from Gui.main_menu import GameMenuWindow
            self.menu_window = GameMenuWindow(self.username)
            self.menu_window.show()    
                
    def update_stats_after_game(self, result, gamemode):
        gamemode = self.gamemode
        """Обновление статистики игрока после игры"""
        if self.username:
            if result == "win":
                self.db.update_stats(self.username, result, gamemode)
            elif result == 'loss':
                self.db.update_stats(self.username, result, gamemode)
            elif result == 'draw':
                    self.db.update_stats(self.username, result, gamemode)

    def check_game_over(self):
        """Проверяет, закончилась ли игра, и обновляет статистику"""
        print("check_gameover вызван")
        board = self.game.board
        current_color = board.current_player
        print(f"Проверка мата для {current_color}: {board.is_checkmate(current_color)}")             
        if board.is_checkmate(current_color):
            self.game_over = True
            loser_color = current_color
            winner_color = 'black' if loser_color == 'white' else 'white'
            
            if hasattr(self, 'network') and self.network and self.network.is_connected():
                if (winner_color == 'white' and self.network.am_i_white) or \
                (winner_color == 'black' and not self.network.am_i_white):
                    result = 'win'
                else:
                    result = 'loss'
                self.update_stats_after_game(result, self.gamemode)
            
            self.update_board()
            self.stop_timers()
            
            if self.network:
                self.show_game_result_dialog(f"Шах и мат!\nПобедили {winner_color}!")
            else:
                QMessageBox.information(self, "Шах и мат!", f"Победили {winner_color}!", QMessageBox.StandardButton.Ok)
                self.offer_rematch()
            return True
            
        elif board.is_stalemate(current_color):
            self.game_over = True
            if hasattr(self, 'network') and self.network and self.network.is_connected():
                self.update_stats_after_game('draw', self.gamemode)
            self.update_board()
            self.stop_timers()
            if self.network:
                self.show_game_result_dialog(f"Ничья!")
            else:
                QMessageBox.information(self, "Пат!", "Ничья!", QMessageBox.StandardButton.Ok)
                self.offer_rematch()
            return True
            
        return False
    
    def stop_timers(self):
        self.timer_engine_white.stop()
        self.timer_engine_black.stop()
        
    def resign_game(self):
        """Сдаться в текущей партии"""
        reply = QMessageBox.question(
            self,
            "Сдача",
            "Вы уверены, что хотите сдаться?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            if hasattr(self, 'network') and self.network and self.network.is_connected():
                self.game_over = True
                self.network.send_resign()
                result = 'loss'
                self.update_stats_after_game(result, self.gamemode)
                self.timer_engine_white.stop()
                self.timer_engine_black.stop()
            # Предложить новую игру
            self.show_game_result_dialog("Вы проиграли!")
            
    def offer_rematch(self):
        """Предлагает сыграть ещё раз"""
        reply = QMessageBox.question(
            self,
            "Игра окончена",
            "Сыграть ещё раз?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.reset_game()
        else:
            self.exit_to_menu()
                  
    def on_opponent_resign(self):
        """Противник сдался"""
        self.game_over = True
        self.update_stats_after_game('win', self.gamemode)
        self.show_game_result_dialog("Противник сдался! Вы победили!")
        
    def update_network_status(self, message):
        """ОБНОВА СТАТУСА СЕТИ"""
        
        self.network_status.setText(message)
        if "ошибка" in message.lower():
            self.network_status.setStyleSheet("color: red; font-weight: bold;")
        elif "подключ" in message.lower():
            self.network_status.setStyleSheet("color: green; font-weight: bold;")
        else:
            self.network_status.setStyleSheet("color: blue; font-weight: bold;")
    
    def on_opponent_connected(self):
        """ПРОТИВНИК ПОДКЛЛЮЧИЛСЯ"""
        
        self.update_network_status("Противник в игре!")
        
        my_color = "белые" if self.network.am_i_white else "чёрные"
        self.statusBar().showMessage(f"Жди пока походит противник!.", 3000)
        
        # ОБНОВА СТАТУСА ХОДА
        self.update_turn_status()
        
        QMessageBox.information(self, "Сеть", 
                            f"Противник подключился!\nТы играешь {my_color}.")
    
    def on_opponent_disconnected(self):
        """ПРОТИВНИК ОТРУБИЛСЯ"""
        if hasattr(self, 'network') and self.network and self.network.is_connected():
            if not self.is_exiting:
                self.update_stats_after_game('win', self.gamemode)
                QMessageBox.warning(self, "Сеть", "Противник отключился. Игра прервана.")
        
    def update_turn_status(self):
        """ПОКАЗЫВАЕТ ЧЕЙ ЩА ХОД"""
        
        if hasattr(self, 'network') and self.network and self.network.is_connected:
            current = self.game.board.current_player
            i_should_move = (current == "white" and self.network.am_i_white) or \
                            (current == "black" and not self.network.am_i_white)
            
            if i_should_move:
                self.statusBar().showMessage(f"ТВОЙ ХОД! ({current})", 2000)
            else:
                self.statusBar().showMessage(f"ЖДИ... Ход {current}", 2000)
        else:
            # ОБЫЧНАЯ ИГРУЛЬКА БЕЗ СЕТИ
            self.statusBar().showMessage(f"Ход: {self.game.board.current_player}", 2000)
        
    def on_network_move(self, from_pos, to_pos):
        """ПОЛУЧЕН ХОД ОТ ПРОТИВНИКА"""
        
        print(f"Получен ход от противника: {from_pos}→{to_pos}")
        success = self.game.board.move_piece(from_pos, to_pos)
        if success:
            self.update_board()
            self.update_turn_status()
            self.update_timer()
            self.statusBar().showMessage(f"Ход противника: {from_pos}→{to_pos}", 2000)
            if self.check_game_over():
                return
            
    def update_timer(self):
        if self.game.board.current_player == "white":
            self.timer_engine_white.start(100)
            self.timer_engine_black.stop()
        elif self.game.board.current_player == "black":
            self.timer_engine_black.start(100)
            self.timer_engine_white.stop()
        else:
            pass
        
    def show_promotion_dialog(self, color):
        """Показывает диалог выбора фигуры"""
        dialog = PromotionDialog(self, color)
        if dialog.exec():
            return dialog.selected_piece
        return None

    def select_piece(self, piece_type, dialog, selected):
        """Выбрана фигура"""
        selected[0] = piece_type
        dialog.accept()
    
    def on_square_click(self, row, col):
        """ПЕРЕДАЕМ КООРДИНАТЫ"""
        if self.game_over:
            print("Игра окончена, ходить нельзя!")
            return
        print(f"Клик: {row}, {col}")
        # ПРОВЕРКА ОЧЕРЕДИ ДЛЯ СЕТЕВОЙ ИГРЫ
        if hasattr(self, 'network') and self.network and self.network.is_connected():
            current = self.game.board.current_player
            i_should_move = (current == "white" and self.network.am_i_white) or \
                            (current == "black" and not self.network.am_i_white)
            
            if not i_should_move: # ПОКАЗЫВАЕТ, ЧТОБЫ ТЫ ПОДОЖДАЛ ПОКА ПОХОДИТ ДРУГОЙ (ДЛЯ СЕТЕВОЙ ИГРЫ)
                print(f"Сейчас ход {current}, жди!")
                self.statusBar().showMessage(f"Сейчас ход {current}, жди!", 2000)
                return
        
        if self.selected_square: #ВЫБРАНА КЛЕТКА
            from_row, from_col = self.selected_square #ЧИСТО БЕРЕМ ПОДСВЕЧЕННУЮ КЛЕТКУ КАК ИСХОДНУЮ ПОЗИЦИЮ
            from_pos = self.index_to_notation(from_row, from_col) #ПЕРЕВОДИМ В ШАХМАТНУЮ НОТАЦИЮ
            to_pos = self.index_to_notation(row, col) #ПЕРЕВОДИМ В ШАХМАТНУЮ НОТАЦИЮ ТАКУЮ ПОЗИЦИЮ, КУДА ХОТИМ ПОХОДИТЬ
            
            success = self.game.board.move_piece(from_pos, to_pos) #УДАЧНЫЙ ХОД
            
            if success: #ЕСЛИ УДАЧНЫЙ ХОД, ТО ОТПРАВЛЯЕМ ХОД СОПЕРНИКУ, УБИРАЕМ ПОДСВЕТКУ КЛЕТКИ И ОБНОВЛЯЕМ ДОСКУ
                
                # Проверяем превращение
                piece = self.game.board.board[row][col]
                if isinstance(piece, Pawn):
                    if (piece.color == "white" and row == 0) or (piece.color == "black" and row == 7):
                        # Показываем диалог
                        new_piece_type = self.show_promotion_dialog(piece.color)
                        
                        if new_piece_type:
                            # Заменяем пешку
                            if new_piece_type == "queen":
                                self.game.board.board[row][col] = Queen(piece.color)
                            elif new_piece_type == "rook":
                                self.game.board.board[row][col] = Rook(piece.color)
                            elif new_piece_type == "bishop":
                                self.game.board.board[row][col] = Bishop(piece.color)
                            elif new_piece_type == "knight":
                                self.game.board.board[row][col] = Knight(piece.color)
                            self.update_board()
                            
                
                print(f"Ход {from_pos}→{to_pos} успешен!")
                self.update_timer()
            if hasattr(self, 'network') and self.network and self.network.is_connected():
                self.network.send_move(from_pos, to_pos)
                self.statusBar().showMessage(f"Ход отправлен: {from_pos}→{to_pos}", 2000)
                
                self.selected_square = None
                self.update_board()
            if self.check_game_over():
                return
             
            else:
                print("Ход невозможен")
                self.selected_square = None
                self.update_board() #ТУТ ПРОСТО ОТМЕНЯЕМ ПОДСВЕТКУ И ВСЕ
                
                piece = self.game.board.board[row][col]
                if piece and piece.color == self.game.board.current_player:
                    self.selected_square = (row, col)
                    self.highlight_square(row, col, True) #Это нужно для того, чтобы ты мог переключаться между своими фигурами одним кликом
        
        else:
            piece = self.game.board.board[row][col]
            if piece and piece.color == self.game.board.current_player:
                self.selected_square = (row, col)
                self.highlight_square(row, col, True) #Тоже самое
            
    def highlight_square(self, row, col, highlight):
        """ПОДСВЕТКА КЛЕТКИ КОТОРУЮ ВЫ ВЫБРАЛИ"""
        
        if highlight:
            self.squares[row][col].setStyleSheet(
                "background-color: yellow; border: 2px solid red; font-size: 40px;"
            )
        else:
            is_light = (row + col) % 2 == 0
            color = "#f0d9b5" if is_light else "#b58863"
            self.squares[row][col].setStyleSheet(
                f"background-color: {color}; border: 1px solid #8b4513; font-size: 40px;"
            )
    
    def update_board(self):
        for row in range(8):
            for col in range(8):
                piece = self.game.board.board[row][col]
                square = self.squares[row][col]
                
                self.highlight_square(row, col, False)
                
                if piece:
                    # ИСПРАВЛЕНО: используем resource_path
                    filename = resource_path(f"Assets/{piece.color}_{piece.piece_type}.png")
                    
                    if os.path.exists(filename):
                        pixmap = QPixmap(filename)
                        if not pixmap.isNull():
                            scaled_pixmap = pixmap.scaled(60, 60, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                            square.setPixmap(scaled_pixmap)
                            square.setText("")
                        else:
                            square.setText(str(piece))
                            square.setPixmap(QPixmap())
                    else:
                        square.setText(str(piece))
                        square.setPixmap(QPixmap())
                else:
                    square.setPixmap(QPixmap())
                    square.setText("")
        
        self.update_turn_status()

    
    def index_to_notation(self, row, col):
        col_letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        return f"{col_letters[col]}{8 - row}"
    