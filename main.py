import os
import telebot
from flask import Flask, request
import threading

# Проверка обязательных переменных
required_envs = [
    'BOT_TOKEN',
    'DEVELOPER_CHAT_ID',
    'WELCOME_MESSAGE',
    'FEEDBACK_MESSAGE'
]
for env in required_envs:
    if not os.getenv(env):
        raise ValueError(f"{env} не установлен!")

# Инициализация бота
bot = telebot.TeleBot(os.getenv('BOT_TOKEN'))
DEVELOPER_CHAT_ID = os.getenv('DEVELOPER_CHAT_ID')


# Обработка текстовых сообщений
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
        # Благодарность пользователю
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


def run_bot():
    print("Запуск Telegram бота...")
    bot.polling(none_stop=True)


if __name__ == '__main__':
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.start()

    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)