from flask import Flask, request, jsonify
from datetime import datetime
import os
import json
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)

class PerevalDatabase:
    def __init__(self):
        self.db_host = os.getenv('FSTR_DB_HOST')
        self.db_port = os.getenv('FSTR_DB_PORT', 5432)
        self.db_login = os.getenv('FSTR_DB_LOGIN')
        self.db_pass = os.getenv('FSTR_DB_PASS')
        self.db_name = "fstr_db"
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

pereval_db = PerevalDatabase()

@app.route('/submitData', methods=['POST'])
def submit_data():
    data = request.json
    required_fields = ['beauty_title', 'title', 'coords', 'user', 'level', 'images']
    for field in required_fields:
        if field not in data:
            return jsonify({
                'status': 400,
                'message': f'Missing field: {field}',
                'id': None
            }), 400

    raw_data = {
        "beautyTitle": data.get('beauty_title'),
        "title": data.get('title'),
        "other_titles": data.get('other_titles', ''),
        "connect": data.get('connect', ''),
        "add_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "user": data.get('user'),
        "coords": data.get('coords'),
        "level": data.get('level')
    }

    images = data.get('images', [])
    pereval_id = pereval_db.add_pereval(raw_data, images)

    if pereval_id:
        return jsonify({
            'status': 200,
            'message': None,
            'id': pereval_id
        })
    else:
        return jsonify({
            'status': 500,
            'message': 'Database error',
            'id': None
        }), 500

# Реализация новых маршрутов
@app.route('/submitData/<int:id>', methods=['GET'])
def get_pereval(id):
    try:
        cursor = pereval_db.connection.cursor(cursor_factory=RealDictCursor)
        query = """
        SELECT * FROM "public"."pereval_added" WHERE "id" = %s;
        """
        cursor.execute(query, (id,))
        result = cursor.fetchone()
        
        if result:
            return jsonify({
                'status': 200,
                'data': result
            })
        else:
            return jsonify({
                'status': 404,
                'message': 'Record not found'
            }), 404
    except Exception as e:
        return jsonify({
            'status': 500,
            'message': str(e)
        }), 500

@app.route('/submitData/<int:id>', methods=['PATCH'])
def patch_pereval(id):
    data = request.json
    
    required_fields = ['beauty_title', 'title', 'coords', 'user', 'level', 'images']
    for field in required_fields:
        if field not in data:
            return jsonify({
                'status': 400,
                'message': f'Missing field: {field}'
            }), 400
    
    try:
        cursor = pereval_db.connection.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
        SELECT "status" FROM "public"."pereval_added" WHERE "id" = %s;
        """, (id,))
        result = cursor.fetchone()
        
        if not result or result['status'] != 'new':
            return jsonify({
                'state': 0,
                'message': 'Cannot edit record: status is not "new"'
            }), 400
        
        query = """
        UPDATE "public"."pereval_added"
        SET "raw_data" = %s, "images" = %s
        WHERE "id" = %s;
        """
        raw_data = {
            "beautyTitle": data.get('beauty_title'),
            "title": data.get('title'),
            "other_titles": data.get('other_titles', ''),
            "connect": data.get('connect', ''),
            "add_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "user": data.get('user'),
            "coords": data.get('coords'),
            "level": data.get('level')
        }
        
        cursor.execute(query, (json.dumps(raw_data), json.dumps(data.get('images', [])), id))
        pereval_db.connection.commit()

        return jsonify({
            'state': 1,
            'message': 'Record updated successfully'
        })
    except Exception as e:
        return jsonify({
            'state': 0,
            'message': str(e)
        }), 500

@app.route('/submitData/', methods=['GET'])
def get_perevals_by_user_email():
    email = request.args.get('user__email')
    
    if not email:
        return jsonify({
            'status': 400,
            'message': 'Missing email parameter'
        }), 400
    
    try:
        cursor = pereval_db.connection.cursor(cursor_factory=RealDictCursor)
        query = """
        SELECT * FROM "public"."pereval_added" 
        WHERE "raw_data"->>'user'->>'email' = %s;
        """
        cursor.execute(query, (email,))
        results = cursor.fetchall()

        if results:
            return jsonify({
                'status': 200,
                'data': results
            })
        else:
            return jsonify({
                'status': 404,
                'message': 'No records found for this email'
            }), 404
    except Exception as e:
        return jsonify({
            'status': 500,
            'message': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True)
