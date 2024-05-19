from flask import Flask, request, jsonify
import sqlite3, os

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

@app.route('/subscriptions/<string:username>')
def subscriptions(username):
    cursor.execute("SELECT followed FROM subscribers WHERE follower = ?", (username,))
    data = cursor.fetchall()
    return jsonify(data)

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
    return jsonify(data)

@app.route('/subscribe/<string:follower>/<string:followed>')
def subscribe(follower, followed):
    cursor.execute("INSERT INTO subscribers (follower, followed) VALUES (?, ?)", (follower, followed))
    connection.commit()
    return jsonify({'message': 'post added successfuly'}), 200

@app.route('/unsubscribe/<string:follower>/<string:followed>')
def unsubscribe(follower, followed):
    cursor.execute("DELETE FROM subscribers WHERE follower = ? AND followed = ?", (follower, followed))
    connection.commit()
    return jsonify({'message': 'post added successfuly'}), 200

if __name__ == '__main__':
    app.run(port=5002, debug=True)