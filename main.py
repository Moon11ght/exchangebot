import config
import telebot
import json
from httplib2 import Http
import requests
import sqlite3

api_key1=config.telegram_api_key
api_key2=config.exchange_api_key
bot = telebot.TeleBot(api_key1)

user_data = {}

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Привіт! Введіть суму для обміну:')
    bot.register_next_step_handler(message, get_amount)

# Отримання суми від користувача
def get_amount(message):
    try:
        amount = float(message.text.strip()) 
        user_data['amount'] = amount
        bot.send_message(message.chat.id, 'Яку валюту ти хочеш обміняти? (наприклад, USD, EUR, UAH)')
        bot.register_next_step_handler(message, get_from_currency)
    except ValueError:
        bot.send_message(message.chat.id, "Будь ласка, введіть правильну суму (число).")
        bot.register_next_step_handler(message, get_amount)

def get_from_currency(message):
    user_data['from_currency'] = message.text.strip().upper() 
    bot.send_message(message.chat.id, 'В яку валюту хочеш поміняти? (наприклад, EUR, USD)')
    bot.register_next_step_handler(message, get_to_currency)

def get_to_currency(message):
    user_data['to_currency'] = message.text.strip().upper() 
    amount = user_data['amount']
    from_currency = user_data['from_currency']
    to_currency = user_data['to_currency']
    
    # Переведення валюти
    result = convert_currency(from_currency, to_currency, amount)
    
    if result:
        bot.send_message(message.chat.id, f"{amount} {from_currency} = {result} {to_currency}")
    else:
        bot.send_message(message.chat.id, "Помилка при отриманні курсу валют. Спробуйте пізніше.")

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