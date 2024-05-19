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
            register_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            gender VARCHAR(40),
            avatar TEXT
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
        user.gender = user_data[6]
        user.avatar = user_data[7]
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
            user.gender = user_data[6]
            user.avatar = user_data[7]
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
        gender = request.form['gender']
        if gender == 'М':
            avatar = r'static\media\imgages\man.png'
        else:
            avatar = r'static\media\imgages\woman.png'
        hashed_password = generate_password_hash(password)
        try:
            cursor.execute('INSERT INTO users (username, useremail, password, gender, avatar) VALUES (?, ?, ?, ?, ?)',
                           (username, useremail, hashed_password, gender, avatar))
            connection.commit()
            cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
            user_data = cursor.fetchone()
            user = User()
            user.id = user_data[0]
            user.username = user_data[1]
            user.useremail = user_data[2]
            user.status = user_data[4]
            user.gender = user_data[6]
            user.avatar = user_data[7]
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
                message = f"Ошибка добавления новости."
        except Exception as e:
            message = f'Произошла ошибка подклчения к серверу. {e}'
    return render_template('add_post.html', message=message)

@app.route('/post/<string:url>')
def view_post(url):
    try:
        response = requests.get(f'{POSTS_MICROSERVICE}/post/{url}')
        if response.status_code == 200:
            post = response.json()
            print(post)
            if current_user.is_authenticated:
                if current_user.username == post[4]:
                    status = 'self sub'
                else:
                    try:
                        response = requests.get(f'{NOTIFICATION_MICROSERVICE}/is_subscribe/{current_user.username}/{post[4]}')
                        if response.json() == [0]:
                            status = 'un sub'
                        else:
                            status = 'sub'
                    except Exception as e:
                        status = e
            else:
                status = 'not authorized'
            return render_template('post.html', post=post, status=status)
        else:
            error = 'Failed to connect to the server'
        return error
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

    try:
        response = requests.get(f'{POSTS_MICROSERVICE}/top_posts')
        if response.status_code == 200:
            top_posts = response.json()
        else:
            top_posts = []
    except Exception:
        top_posts = []

    if current_user.is_authenticated:
        userid = current_user.id
        if current_user.status == 'admin':
            status = True
        else:
            status = False
    else:
        userid = None
        status = False
    return render_template('main.html', data=data, status=status, top_posts=top_posts, userid=userid)

@app.route('/profile/<string:userid>')
@login_required
def profile(userid):
    cursor.execute("SELECT * FROM users WHERE id = ?", (userid,))
    data = cursor.fetchone()
    return render_template('profile.html', data=data)

@app.route('/feed')
def feed():
    try:
        response = requests.get(f'{POSTS_MICROSERVICE}/feed')
        if response.status_code == 200:
            feed = response.json()
        else:
            feed = []
    except Exception:
        feed = []
    return render_template('feed.html', feed=feed)
    

if __name__ == '__main__':
    app.run(debug=True)
