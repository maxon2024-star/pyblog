from models import db, User, Post
from app import app
from datetime import datetime

with app.app_context():
    # Очистка таблиц (опционально)
    db.drop_all()
    db.create_all()

    # Добавление тестовых пользователей
    user1 = User(username='Alice', email='alice@example.com', password='hashed_password_1')
    user2 = User(username='Bob', email='bob@example.com', password='hashed_password_2')

    db.session.add(user1)
    db.session.add(user2)

    # Добавление тестовых постов
    post1 = Post(title='My First Post', content='This is my first blog post!', date_posted=datetime.utcnow(), author=user1)
    post2 = Post(title='A Post from Bob', content='Hello from Bob!', date_posted=datetime.utcnow(), author=user2)

    db.session.add(post1)
    db.session.add(post2)

    db.session.commit()
    print('Database populated successfully!')
