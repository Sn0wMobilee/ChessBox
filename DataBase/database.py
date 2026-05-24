import sqlite3
import hashlib
from DataBase.config import DB_PATH
import sys
import os
def get_db_path():
    """Возвращает путь к БД в зависимости от способа запуска"""
    if getattr(sys, 'frozen', False):
        # Запущено как exe - БД рядом с программой
        return os.path.join(os.path.dirname(sys.executable), 'chess_stats.db')
    else:
        # Запущено как скрипт - БД в папке
        return DB_PATH
class Database:
    """Класс для работы с БД"""
    
    def __init__(self):
        self.db_path = get_db_path()
        self.create_tables()
    
    def create_tables(self):
        """Создаёт таблицы, если их нет"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                bullet_wins INTEGER DEFAULT 0,
                bullet_losses INTEGER DEFAULT 0,
                bullet_draws INTEGER DEFAULT 0,
                blitz_wins INTEGER DEFAULT 0,
                blitz_losses INTEGER DEFAULT 0,
                blitz_draws INTEGER DEFAULT 0,
                rapid_wins INTEGER DEFAULT 0,
                rapid_losses INTEGER DEFAULT 0,
                rapid_draws INTEGER DEFAULT 0,
                endless_wins INTEGER DEFAULT 0,
                endless_losses INTEGER DEFAULT 0,
                endless_draws INTEGER DEFAULT 0
                
            )
        ''')
        conn.commit()
        conn.close()
    
    def hash_password(self, password: str) -> str:
        """Хеширует пароль"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def register_user(self, username: str, password: str) -> tuple:
        """
        Регистрирует нового пользователя
        Возвращает: (успех, сообщение)
        """
        username = username.strip()
        
        if not username or not password:
            return False, "Заполните все поля!"
        
        if len(password) < 4:
            return False, "Пароль должен быть минимум 4 символа!"
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        #Проверяем существует ли пользователь
        cursor.execute("SELECT * FROM Users WHERE name = ?", (username,))
        if cursor.fetchone():
            conn.close()
            return False, "Имя пользователя уже занято!"
        
        # Регистрируем
        password_hash = self.hash_password(password)
        cursor.execute(
            "INSERT INTO Users (name, password) VALUES (?, ?)",
            (username, password_hash)
        )
        conn.commit()
        conn.close()
        
        return True, "Регистрация успешна!"
    
    def login_user(self, username: str, password: str) -> tuple:
        """
        Вход пользователя
        Возвращает: (успех, данные_пользователя_или_сообщение)
        """
        username = username.strip()
        
        if not username or not password:
            return False, "Заполните все поля!"
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Users WHERE name = ?", (username,))
        user = cursor.fetchone()
        conn.close()
        
        if user and self.hash_password(password) == user[2]:
            # user: (id, name, password, wins, losses, draws)
            return True, user
        return False, "Неверное имя или пароль!"
    
    def get_stats(self, username: str) -> dict:
        """
        Получает статистику пользователя
        Возвращает: словарь с wins, losses, draws или None
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """SELECT bullet_wins, bullet_losses, bullet_draws,
            blitz_wins, blitz_losses, blitz_draws,
            rapid_wins, rapid_losses, rapid_draws,
            endless_wins, endless_losses, endless_draws FROM Users WHERE name = ?""",
            (username,)
        )
        stats = cursor.fetchone()
        conn.close()
        
        if stats:
            return {
                "bullet_wins": stats[0],
                "bullet_losses": stats[1],
                "bullet_draws": stats[2],
                "blitz_wins": stats[3],
                "blitz_losses": stats[4],
                "blitz_draws": stats[5],
                "rapid_wins": stats[6],
                "rapid_losses": stats[7],
                "rapid_draws": stats[8],
                "endless_wins": stats[9],
                "endless_losses": stats[10],
                "endless_draws": stats[11],
                "total_wins": stats[0] + stats[3] + stats[6] + stats[9],
                "total_losses": stats[1] + stats[4] + stats[7] + stats[10],
                "total_draws": stats[2] + stats[5] + stats[8] + stats[11]
            }
        return None
    
    def update_stats(self, username: str, result: str, gamemode: str) -> None:
        """
        Обновляет статистику после игры
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if gamemode == 'bullet':
            if result == 'win':
                cursor.execute(
                    "UPDATE Users SET bullet_wins = bullet_wins + 1 WHERE name = ?",
                    (username,)
                )
            elif result == 'loss':
                cursor.execute(
                "UPDATE Users SET bullet_losses = bullet_losses + 1 WHERE name = ?",
                (username,)
            )
            elif result == 'draw':
                cursor.execute(
                    "UPDATE Users SET bullet_draws = bullet_draws + 1 WHERE name = ?",
                    (username,)
                )
                
        elif gamemode == 'blitz':
            if result == 'win':
                cursor.execute(
                    "UPDATE Users SET blitz_wins = blitz_wins + 1 WHERE name = ?",
                    (username,)
                )
            elif result == 'loss':
                cursor.execute(
                "UPDATE Users SET blitz_losses = blitz_losses + 1 WHERE name = ?",
                (username,)
            )
            elif result == 'draw':
                cursor.execute(
                    "UPDATE Users SET blitz_draws = blitz_draws + 1 WHERE name = ?",
                    (username,)
                )
        elif gamemode == 'rapid':
            if result == 'win':
                cursor.execute(
                    "UPDATE Users SET rapid_wins = rapid_wins + 1 WHERE name = ?",
                    (username,)
                )
            elif result == 'loss':
                cursor.execute(
                "UPDATE Users SET rapid_losses = rapid_losses + 1 WHERE name = ?",
                (username,)
            )
            elif result == 'draw':
                cursor.execute(
                    "UPDATE Users SET rapid_draws = rapid_draws + 1 WHERE name = ?",
                    (username,)
                )
        elif gamemode == 'endless':
            if result == 'win':
                cursor.execute(
                    "UPDATE Users SET endless_wins = endless_wins + 1 WHERE name = ?",
                    (username,)
                )
            elif result == 'loss':
                cursor.execute(
                "UPDATE Users SET endless_losses = endless_losses + 1 WHERE name = ?",
                (username,)
            )
            elif result == 'draw':
                cursor.execute(
                    "UPDATE Users SET endless_draws = endless_draws + 1 WHERE name = ?",
                    (username,)
                )
        conn.commit()
        conn.close()
    
    # def get_all_users(self) -> list:
    #     """Возвращает список всех пользователей (для таблицы лидеров)"""
    #     conn = sqlite3.connect(self.db_path)
    #     cursor = conn.cursor()
    #     cursor.execute(
    #         "SELECT name, wins, losses, draws FROM Users ORDER BY wins DESC"
    #     )
    #     users = cursor.fetchall()
    #     conn.close()
    #     return users
    
    def auto_login(self, username):
        """Автоматический вход по имени (без проверки пароля)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Users WHERE name = ?", (username,))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return True, user
        return False, "Пользователь не найден"
    
    def delete_user(self, username: str) -> bool:
        """Удаляет пользователя (для администрирования)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Users WHERE name = ?", (username,))
        affected = cursor.rowcount
        conn.commit()
        conn.close()
        return affected > 0