from flask import Flask, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash,  check_password_hash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import sqlite3, os, requests

app = Flask(__name__)
app.secret_key = 'secretik'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

POSTS_MICROSERVICE = 'http://127.0.0.1:5001'
NOTIFICATION_MICROSERVICE = 'http://127.0.0.1:5002'

db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'users.db')

connection = sqlite3.connect(db_path, check_same_thread=False)
cursor = connection.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY, 
            username TEXT UNIQUE, 
            useremail TEXT UNIQUE,
            password TEXT,
            status TEXT DEFAULT user,
            register_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''')
connection.commit()

class User(UserMixin):
    pass

@login_manager.user_loader
def load_user(user_id):
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user_data = cursor.fetchone()
    if user_data:
        user = User()
        user.id = user_data[0]
        user.username = user_data[1]
        user.useremail = user_data[2]
        user.status = user_data[4]
        return user
    return None

@app.route('/login', methods = ['POST', 'GET'])
def login():
    error = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user_data = cursor.fetchone()
        if user_data and check_password_hash(user_data[3], password):
            user = User()
            user.id = user_data[0]
            user.username = user_data[1]
            user.useremail = user_data[2]
            user.status = user_data[4]
            login_user(user, remember=True)
            return redirect(url_for('index'))
        else:
            error = 'Пользователь с таким логином и паролем не найден'
    return render_template('login.html', error=error)

@app.route('/register', methods = ['POST', 'GET'])
def register():
    error = ''
    if request.method == 'POST':
        username = request.form['username']
        useremail = request.form['useremail']
        password = request.form['password']
        hashed_password = generate_password_hash(password)
        try:
            cursor.execute('INSERT INTO users (username, useremail, password) VALUES (?, ?, ?)',
                           (username, useremail, hashed_password))
            connection.commit()
            cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
            user_data = cursor.fetchone()
            user = User()
            user.id = user_data[0]
            user.username = user_data[1]
            user.useremail = user_data[2]
            user.status = user_data[4]
            login_user(user, remember=True)
            return redirect(url_for('index'))
        except sqlite3.IntegrityError:
            error = 'Пользователь с таким логином уже существует'
    return render_template('register.html', error=error)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/add_post', methods = ['POST', 'GET'])
@login_required
def add_post():
    message = ''
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        url = f'{current_user.username}_{title}'
        url = url.replace(' ', '_').lower()
        payload = {
            'title': title,
            'url': url,
            'username': current_user.username,
            'content': content,
        }
        try:
            response = requests.post(f'{POSTS_MICROSERVICE}/add_post', json=payload)
            if response.status_code == 200:
                message = 'Новость успешно добавлена'
            else:
                message = f'Ошибка добавления новости. {response.json().get('message')}'
        except Exception as e:
            message = f'Произошла ошибка подклчения к серверу. {e}'
    return render_template('add_post.html', message=message)

@app.route('/post/<string:url>')
def view_post(url):
    try:
        response = requests.get(f'{POSTS_MICROSERVICE}/post/{url}')
        if response.status_code == 200:
            post = response.json()
            return render_template('post.html', post=post)
        else:
            print(f'An error occurred on the server {response.status_code}') 
            return 'sosi' 
    except Exception:
        error = 'Failed to connect to the server'
        return error 

@login_required
@app.route('/admin')
def admin():
    if current_user.status == 'admin':
        return render_template('admin.html')
    else:
        return redirect(url_for('index'))

@app.route('/') 
def index():
    try:
        response = requests.get(f'{POSTS_MICROSERVICE}/my_posts/{current_user.username}')
        if response.status_code == 200:
            data = response.json()
        else:
            data = []
    except Exception:
        data = [['', 'Хм... Похоже вы не создали еще ни одного поста']]
    if current_user.is_authenticated and current_user.status == 'admin':
        status = True
    else:
        status = False
    return render_template('main.html', data=data, status=status)

@app.route('/profile')
@login_required
def profile():
    data = [current_user.username, current_user.useremail, current_user.status]
    return render_template('profile.html', data=data)

if __name__ == '__main__':
    app.run(debug=True)
