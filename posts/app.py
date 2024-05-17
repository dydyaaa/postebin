from flask import Flask, request, jsonify
import sqlite3, os, redis, json

app = Flask(__name__)

db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'posts.db')
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

connection = sqlite3.connect(db_path, check_same_thread=False)
cursor = connection.cursor()

cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS posts(
    id INTEGER PRIMARY KEY,
    title VARCHAR(50),
    url VARACAR(100),
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(50),
    content_sourse TEXT)"""
)

@app.route('/add_post', methods=['POST', 'GET'])
def add_post():
    data = request.get_json()
    title = data.get('title')
    url = data.get('url')
    username = data.get('username')
    content = data.get('content')
    if title and url and username and content:
        cursor.execute("SELECT COUNT(*) FROM posts WHERE title = ?", (title,))
        if cursor.fetchone()[0] > 0:
            return jsonify({'message': 'Пост с таким названием уже существует'}), 401
        content_sourse = os.path.join('Posts_source', f"{url}.txt")
        with open(content_sourse, 'w') as file:
            file.write(content)
        cursor.execute(
            "INSERT INTO posts (title, url, created_by, content_sourse) VALUES (?, ?, ?, ?)",
            (title, url, username, content_sourse,)
        )
        connection.commit()
        return jsonify({'message': 'post added successfuly'}), 200
    else:
        return jsonify({'message': 'Invalid data'}), 400

@app.route('/post/<string:url>')
def view_post(url):
    cache_key = url
    cache_post = redis_client.get(cache_key)
    if cache_post:
        data = json.loads(cache_post)
        redis_client.expire(cache_key, 180)
        print(f'data from redis')
        return jsonify(data)
    else:
        cursor.execute("SELECT * FROM posts WHERE url = ?", (url,))
        data = cursor.fetchone()
        redis_client.setex(cache_key, 180, json.dumps(data))
        print(f'data from sql')
        return jsonify(data)

if __name__ == '__main__':
    app.run(port=5001, debug=True)