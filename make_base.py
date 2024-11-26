import psycopg2

def create_database():
    connection = None 
    try:
        # Подключение к PostgreSQL
        connection = psycopg2.connect(
            user="bigz",  # Имя пользователя PostgreSQL
            password="05062012",  # Пароль
            host="localhost",  # Хост, на котором работает PostgreSQL
            port="5432",  # Порт PostgreSQL
            dbname = "pyblog"
        )
        connection.autocommit = True

        # Создание курсора для выполнения SQL-запросов
        cursor = connection.cursor()

        # Создание базы данных
        cursor.execute("CREATE DATABASE pyblog;")
        print("База данных 'blog_db' успешно создана!")

    except Exception as error:
        print(f"Ошибка при создании базы данных: {error}")

    finally:
        if connection:
            cursor.close()
            connection.close()

if __name__ == "__main__":
    create_database()
