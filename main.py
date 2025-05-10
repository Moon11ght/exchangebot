import config
import telebot
from httplib2 import Http
import requests
from telebot import types

api_key1=config.telegram_api_key
api_key2=config.exchange_api_key
bot = telebot.TeleBot(api_key1)

user_data = {}
state = 0
symbols = {"Crypto":{"Bitcoin":"BTC"},
           "Metals":{"Золото(troy ounce)": "XAU",
           "Срібло(troy ounce)":"XAG"},
           "Currency":{"UAH ₴":"UAH", 
           "USD $":"USD", 
           "EUR €":"EUR", 
           "GBP £":"GBP", 
           "JPY ¥":"JPY",
           "CNY ¥":"CNY", 
           "KZT ₸":"KZT",
           "AED":"AED",
           "PLN Zł":"PLN"}}
@bot.message_handler(commands=['menu'])
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("₿ Криптовалюта")
    btn2 = types.KeyboardButton("¤ Валюта")
    btn3 = types.KeyboardButton("💰 Цінні метали")
    btn4 = types.KeyboardButton("❌ Вийти")
    markup.add(btn1, btn2)
    markup.add(btn3, btn4)
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    user_data[message.chat.id] = [{"state":0}]
    markup = main_menu()
    bot.send_message(message.chat.id, 'Привіт! Обери опцію нижче:', reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == "₿ Криптовалюта")
def crypto_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for currency in list(symbols["Crypto"].keys()):
        markup.add(types.KeyboardButton(currency))
    markup.add(types.KeyboardButton("← Назад"))
    bot.send_message(message.chat.id, "Обери криптовалюту:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "¤ Валюта")
def currency_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    currencies = list(symbols["Currency"].keys())
    
    row = []
    for i, currency in enumerate(currencies, start=1):
        row.append(types.KeyboardButton(currency))
        if i % 3 == 0:
            markup.add(*row)
            row = []
    if row:
        markup.add(*row)

    markup.add(types.KeyboardButton("← Назад"))
    bot.send_message(message.chat.id, "Обери валюту:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "💰 Цінні метали")
def metals_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for currency in list(symbols["Metals"].keys()):
        markup.add(types.KeyboardButton(currency))
    markup.add(types.KeyboardButton("← Назад"))
    bot.send_message(message.chat.id, "Обери метал:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "← Назад")
def back_to_main(message):
    markup = main_menu()
    bot.send_message(message.chat.id,"Повтори дію",reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "❌ Вийти")
def exit_bot(message):
    markup = types.ReplyKeyboardRemove()
    bot.send_message(message.chat.id, "Дякуємо за використання бота!", reply_markup=markup)

@bot.message_handler(func=lambda message:True)
def option_handler(message):
    for item in list(symbols.keys()):
        for currency in symbols[item]:
            if message.text == currency:
                if user_data[message.chat.id][0]["state"] == 0:
                    user_data[message.chat.id].append({"from_currency": symbols[item][currency]})
                    markup = main_menu()
                    bot.send_message(message.chat.id, "На що міняти", reply_markup=markup)
                    user_data[message.chat.id][0]["state"] += 1
                    return

                if user_data[message.chat.id][0]["state"] == 1:
                    user_data[message.chat.id].append({"to_currency": symbols[item][currency]})
                    markup = main_menu()
                    msg = bot.send_message(message.chat.id, "Вкажіть сумму", reply_markup=types.ReplyKeyboardRemove())
                    user_data[message.chat.id][0]["state"] += 1
                    bot.register_next_step_handler(msg, get_amount)
                    return

    if user_data[message.chat.id][0]["state"] == 2:
        msg = bot.send_message(message.chat.id, "Вкажіть сумму:")
        bot.register_next_step_handler(msg, get_amount)

def get_amount(message):
    try:
        amount = float(message.text)
        user_data[message.chat.id].append({"amount": amount})
        result = convert_currency(
            user_data[message.chat.id][1]["from_currency"],
            user_data[message.chat.id][2]["to_currency"],
            amount
        )
        markup = main_menu()
        bot.send_message(message.chat.id, result, reply_markup=markup)
        user_data[message.chat.id].clear()
        user_data[message.chat.id] = [{"state": 0}]

    except ValueError:
        markup = main_menu()
        msg = bot.send_message(message.chat.id, "Вкажіть корректно сумму", reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(msg, get_amount)

def convert_currency(from_currency, to_currency, amount):
    url = f"https://api.apilayer.com/exchangerates_data/convert?to={to_currency}&from={from_currency}&amount={amount}"
    headers = {
        "apikey": api_key2
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if data.get("success"):
            return data.get("result")
    return None

bot.infinity_polling()



