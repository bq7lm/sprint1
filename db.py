import psycopg2
import json
import os
from psycopg2.extras import RealDictCursor

class PerevalDatabase:
    def __init__(self):
        self.db_host = os.getenv('FSTR_DB_HOST')
        self.db_port = os.getenv('FSTR_DB_PORT', 5432)
        self.db_login = os.getenv('FSTR_DB_LOGIN')
        self.db_pass = os.getenv('FSTR_DB_PASS')
        self.db_name = "fstr_db"  # название базы данных

        self.connection = self.connect_db()

    def connect_db(self):
        """Подключение к базе данных PostgreSQL"""
        try:
            connection = psycopg2.connect(
                host=self.db_host,
                port=self.db_port,
                dbname=self.db_name,
                user=self.db_login,
                password=self.db_pass
            )
            return connection
        except Exception as e:
            print(f"Ошибка при подключении к БД: {e}")
            return None

    def add_pereval(self, raw_data, images):
        """Добавление новой записи о перевале в базу данных"""
        try:
            cursor = self.connection.cursor()
            query = """
            INSERT INTO "public"."pereval_added" ("raw_data", "images", "status")
            VALUES (%s, %s, 'new')
            RETURNING id;
            """
            cursor.execute(query, (json.dumps(raw_data), json.dumps(images)))
            pereval_id = cursor.fetchone()[0]
            self.connection.commit()
            return pereval_id
        except Exception as e:
            print(f"Ошибка при добавлении перевала: {e}")
            return None

    def close_connection(self):
        """Закрытие соединения с базой данных"""
        if self.connection:
            self.connection.close()
