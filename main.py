import os
import telebot
from flask import Flask, request, jsonify

# Проверка обязательных переменных
required_envs = [
    'BOT_TOKEN',
    'DEVELOPER_CHAT_ID',
    'WELCOME_MESSAGE',
    'FEEDBACK_MESSAGE',
    'WEBHOOK_URL'
]
for env in required_envs:
    if not os.getenv(env):
        raise ValueError(f"{env} не установлен!")

# Инициализация бота
bot = telebot.TeleBot(os.getenv('BOT_TOKEN'))
DEVELOPER_CHAT_ID = os.getenv('DEVELOPER_CHAT_ID')
WEBHOOK_URL = os.getenv('WEBHOOK_URL')



def get_env_message(env_name):
    message = os.getenv(env_name)
    return message.replace('\\n', '\n')


welcome_message = get_env_message('WELCOME_MESSAGE')
feedback_message = get_env_message('FEEDBACK_MESSAGE')


# Обработчики команд
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, welcome_message)


@bot.message_handler(func=lambda message: True)
def handle_feedback(message):
    try:
        bot.forward_message(
            chat_id=DEVELOPER_CHAT_ID,
            from_chat_id=message.chat.id,
            message_id=message.message_id
        )
        bot.reply_to(message, feedback_message)
    except Exception as e:
        print(f"Ошибка: {e}")
        bot.reply_to(
            message,
            "Произошла ошибка при отправке. Пожалуйста, попробуйте позже."
        )


app = Flask(__name__)


@app.route('/')
def home():
    return "Бот работает!"


@app.route('/webhook', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_data = request.get_json()
        update = telebot.types.Update.de_json(json_data)
        bot.process_new_updates([update])
        return jsonify({"status": "ok"}), 200
    else:
        return jsonify({"error": "Invalid content type"}), 403



def set_webhook():
    try:
        bot.remove_webhook()
        bot.set_webhook(url=WEBHOOK_URL)
        print(f"Вебхук установлен на: {WEBHOOK_URL}")
    except Exception as e:
        print(f"Ошибка установки вебхука: {e}")


if __name__ == '__main__':

    set_webhook()

    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)