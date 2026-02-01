"""Скрипт для создания начального пользователя в БД"""
from app.database import SessionLocal, engine, Base
from app.models import User
from app.auth import get_password_hash

# Данные пользователя
USERNAME = "albert"
PASSWORD = "Albert1940!"


def seed_user():
    # Создаем таблицы если их нет
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Проверяем, есть ли уже пользователь
        existing_user = db.query(User).filter(User.username == USERNAME).first()
        
        if existing_user:
            print(f"Пользователь '{USERNAME}' уже существует")
            return
        
        # Создаем пользователя
        user = User(
            username=USERNAME,
            password_hash=get_password_hash(PASSWORD)
        )
        db.add(user)
        db.commit()
        
        print(f"Пользователь '{USERNAME}' успешно создан!")
        print(f"Логин: {USERNAME}")
        print(f"Пароль: {PASSWORD}")
        
    finally:
        db.close()


if __name__ == "__main__":
    seed_user()

