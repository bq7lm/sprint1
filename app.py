from flask import Flask, request, jsonify
from datetime import datetime
import os
from db import PerevalDatabase  # Импортируем класс работы с БД

app = Flask(__name__)
pereval_db = PerevalDatabase()

@app.route('/submitData', methods=['POST'])
def submit_data():
    data = request.json

    # Проверка на обязательные поля
    required_fields = [
        'beauty_title', 'title', 'coords', 'user', 'level', 'images'
    ]
    for field in required_fields:
        if field not in data:
            return jsonify({
                'status': 400,
                'message': f'Missing field: {field}',
                'id': None
            }), 400

    # Создание данных для вставки в БД
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

    # Добавление записи в базу данных
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

if __name__ == '__main__':
    app.run(debug=True)
