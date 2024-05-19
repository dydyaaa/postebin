from flask import Flask, request, jsonify
import sqlite3, os, redis, json

app = Flask(__name__)

db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'notification.db')

connection = sqlite3.connect(db_path, check_same_thread=False)
cursor = connection.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS subscribers (
            id INTEGER PRIMARY KEY, 
            follower VARCAHR, 
            followed VARCAHR,
            notification BOOLEAN
            )''')
connection.commit()

@app.route('/subscriptions')
def subscriptions():
    pass

@app.route('/is_subscribe/<string:follower>/<string:followed>')
def subscroptions(follower, followed):
    cursor.execute(
        """
        SELECT COUNT(*)
        FROM subscribers
        WHERE follower = ? AND followed = ?""",
        (follower, followed)
    )
    data = cursor.fetchone()
    print(data)
    return jsonify(data)

if __name__ == '__main__':
    app.run(port=5002, debug=True)