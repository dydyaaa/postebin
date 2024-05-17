import telebot, sqlite3, os

API_TOKEN = '916278807:AAGsNPTB7NkuJ5AKqRX2njl-JrXa-IZiCVI'
bot = telebot.TeleBot(API_TOKEN)

db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'notification.db')
connection = sqlite3.connect(db_path, check_same_thread=False)
cursor = connection.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS notification_tg (
            id INTEGER PRIMARY KEY, 
            user_id INTEGER UNIQUE, 
            user_tg INTEGER UNIQUE
            )''')
connection.commit()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    args = message.text.split()
    if len(args) > 1 and args[1] == '1':
        cursor.execute("INSERT INTO notification_tg (user_id, user_tg)", (args, message.chat.id))
        connection.commit()
        msg = 'Связь с сайтом установлена. \
            Теперь вы будете получать уведомления со своего аккаунта.'
        bot.send_message(message.chat.id, msg)
    else:
        msg = 'Перейдите в настройки аккаунта (https://127.0.0.1/5000/account/settings) \
            Postebin и привяжите Telegram в разделе оповещений.'
        bot.send_message(message.chat.id, msg)

def notificate(message):
    cursor.execute('SELECT user_tg FROM notification_tg',)
    for i in cursor.fetchall():
        print(i[0])

if __name__ == '__main__':
    bot.polling()
