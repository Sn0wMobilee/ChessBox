# Chess/DataBase.py
from database import Database

if __name__ == "__main__":
    db = Database()
    print("Таблицы созданы")
    print(f"База данных: {db.db_path}")