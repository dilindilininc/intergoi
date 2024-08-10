import telebot
from telebot import types

bot = telebot.TeleBot('')


@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("✡ | Список | ✡")
    btn2 = types.KeyboardButton("✡ | Добавить | ✡")
    btn2 = types.KeyboardButton("✡ | Связь | ✡")
    markup.add(btn1, btn2)
    bot.send_message(message.chat.id, text="✡ Шалом, \{0.first_name}\!\nЯ виртуальный агент Интергой!\nНаша организация занимается поиском и отлавливанием гоев и харамников, нарушивших законы Великой Жидомасонской Ложи!\n\n❓ У тебя есть информация о вероятном местонахождении гоя? Ты хочешь отправить жалобу на вероятного гоя? Используй этого бота!\n\n[✡ Связаться с нами](https://t.me/sionatlantida)", parse_mode='Markdown', reply_markup=markup)


@bot.message_handler(content_types=['text'])
def func(message):
    if message.text == "✡ ┇ Связь ┇ ✡":
        bot.send_message(message.chat.id, text="Шалом! По всем вопросам к @sionatlantida)")
    elif message.text == "❓ Задать вопрос":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Как меня зовут?")
        btn2 = types.KeyboardButton("Что я могу?")
        back = types.KeyboardButton("Вернуться в главное меню")
        markup.add(btn1, btn2, back)
        bot.send_message(message.chat.id, text="Задай мне вопрос", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, text="На такую комманду я не запрограммировал..")


bot.polling(none_stop=True)