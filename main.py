import config
import telebot
from telebot import types
from api import convert_currency

api_key1 = config.telegram_api_key
bot = telebot.TeleBot(api_key1)

class State:
    CHOOSE_FROM = "choose_from"
    CHOOSE_TO = "choose_to"
    ENTER_AMOUNT = "enter_amount"

class UserSession:
    def __init__(self):
        self.state = None
        self.from_currency = None
        self.to_currency = None
        self.amount = None

user_data = {}

symbols = {
    "Crypto": {"Bitcoin": "BTC"},
    "Metals": {"Золото(troy ounce)": "XAU", "Срібло(troy ounce)": "XAG"},
    "Currency": {
        "UAH ₴": "UAH", "USD $": "USD", "EUR €": "EUR", "GBP £": "GBP",
        "JPY ¥": "JPY", "CNY ¥": "CNY", "KZT ₸": "KZT", "AED": "AED", "PLN Zł": "PLN"
    }
}
all_symbols = {k: v for group in symbols.values() for k, v in group.items()}

def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("₿ Криптовалюта", "¤ Валюта")
    markup.add("💰 Цінні метали", "❌ Вийти")
    return markup

def generate_submenu(category):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for name in symbols[category].keys():
        markup.add(types.KeyboardButton(name))
    markup.add("← Назад")
    return markup

@bot.message_handler(commands=['start', 'menu'])
def start(message):
    user_data[message.chat.id] = UserSession()
    bot.send_message(message.chat.id, "Привіт! Обери опцію нижче:", reply_markup=main_menu())

@bot.message_handler(commands=['help'])
def help_command(message):
    bot.send_message(message.chat.id, "Цей бот допоможе конвертувати валюту, криптовалюту та метали.\n"
                                      "1️⃣ Оберіть тип валюти\n"
                                      "2️⃣ Оберіть з якої на яку конвертувати\n"
                                      "3️⃣ Введіть суму для обміну")

@bot.message_handler(func=lambda msg: msg.text == "₿ Криптовалюта")
def crypto_menu(message):
    bot.send_message(message.chat.id, "Обери криптовалюту:", reply_markup=generate_submenu("Crypto"))

@bot.message_handler(func=lambda msg: msg.text == "¤ Валюта")
def currency_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    buttons = [types.KeyboardButton(name) for name in symbols["Currency"]]
    markup.add(*buttons)
    markup.add("← Назад")
    bot.send_message(message.chat.id, "Обери валюту:", reply_markup=markup)

@bot.message_handler(func=lambda msg: msg.text == "💰 Цінні метали")
def metals_menu(message):
    bot.send_message(message.chat.id, "Обери метал:", reply_markup=generate_submenu("Metals"))

@bot.message_handler(func=lambda msg: msg.text == "← Назад")
def back_to_main(message):
    user_data[message.chat.id] = UserSession()
    bot.send_message(message.chat.id, "Повертаємось до головного меню:", reply_markup=main_menu())

@bot.message_handler(func=lambda msg: msg.text == "❌ Вийти")
def exit_bot(message):
    bot.send_message(message.chat.id, "Дякуємо за використання бота!", reply_markup=types.ReplyKeyboardRemove())
    user_data.pop(message.chat.id, None)

@bot.message_handler(func=lambda msg: True)
def handle_selection(message):
    chat_id = message.chat.id
    text = message.text
    user = user_data.setdefault(chat_id, UserSession())

    currency_code = all_symbols.get(text)

    if currency_code:
        if user.state is None: 
            user.from_currency = currency_code
            user.state = State.CHOOSE_TO
            bot.send_message(chat_id, "Оберіть валюту, в яку хочете конвертувати:", reply_markup=main_menu())
        elif user.state == State.CHOOSE_TO:
            user.to_currency = currency_code
            user.state = State.ENTER_AMOUNT
            msg = bot.send_message(chat_id, "Введіть суму для конвертації:", reply_markup=types.ReplyKeyboardRemove())
            bot.register_next_step_handler(msg, get_amount)
    elif user.state == State.ENTER_AMOUNT:
        bot.register_next_step_handler(message, get_amount)
    else:
        bot.send_message(chat_id, "Будь ласка, оберіть валюту або метал з меню.")

def get_amount(message):
    chat_id = message.chat.id
    user = user_data.get(chat_id)

    try:

        amount = float(message.text)

        if amount <= 0:
            raise ValueError("Сума повинна бути більше за 0.")
        if amount > 1_000_000:
            raise ValueError("Сума занадто велика. Спробуйте ввести меншу суму.")

        result = convert_currency(user.from_currency, user.to_currency, amount)

        if result > 0:
            exchange_rate = round(result / amount, 2)
            response = (
                f"✅ *Конвертація успішна!*\n"
                f"{amount:.2f} {user.from_currency} → {result:.2f} {user.to_currency}\n"
                f"_Курс_: 1 {user.from_currency} = {exchange_rate:.2f} {user.to_currency}"
            )
            bot.send_message(chat_id, response, parse_mode="Markdown", reply_markup=main_menu())
        else:
            bot.send_message(chat_id, "❌ Сталася помилка при конвертації. Спробуйте знову.", reply_markup=main_menu())

        user_data[chat_id] = UserSession()

    except ValueError as e:
        msg = bot.send_message(chat_id, f"❌ {e}\nСпробуйте ще раз:")
        bot.register_next_step_handler(msg, get_amount)

bot.infinity_polling()