from . import bot
from telebot import types
from datetime import datetime, timedelta
import time
import hashlib


def to_main_page(user, message='✅'):
    user.state = 3
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    info_button = types.KeyboardButton('Информация о боте')
    invest_button = types.KeyboardButton('Инвестирование')
    ref_button = types.KeyboardButton('Реферальная система')
    pay_button = types.KeyboardButton('Выплаты')
    markup.add(info_button, invest_button, ref_button, pay_button)
    bot.send_message(user.id, message, reply_markup=markup)
    user.save()


def to_invest_page(user, message='✅'):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    invest_button = types.KeyboardButton('Инвестировать')
    invest_sum_button = types.KeyboardButton('Инвестированная сумма')
    payed_sum_button = types.KeyboardButton('Выплаченная сумма')
    remind_sum_button = types.KeyboardButton('Остаток по выплатам')
    back_button = types.KeyboardButton('Назад')
    markup.add(invest_button, invest_sum_button, payed_sum_button, remind_sum_button, back_button)
    bot.send_message(user.id, message, reply_markup=markup)


def to_ref_page(user, message='✅'):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    valid_ref_button = types.KeyboardButton('Количество оплативших реералов')
    save_sum_button = types.KeyboardButton('Накопленная сумма')
    id_button = types.KeyboardButton('ID для рефералов')
    back_button = types.KeyboardButton('Назад')
    markup.add(valid_ref_button, save_sum_button, id_button, back_button)
    bot.send_message(user.id, message, reply_markup=markup)


def to_pay_page(user, message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    change = types.KeyboardButton('Изменить')
    back = types.KeyboardButton('Назад')
    markup.add(change, back)
    bot.send_message(user.id, message, reply_markup=markup)


def change_payeer(user):
    user.state = 41
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    back = types.KeyboardButton('Назад')
    markup.add(back)
    bot.send_message(user.id, 'Введите номер вашего кошелька в Payeer.\n\n https://payeer.com/',
                     reply_markup=markup)

def year_from_now():
    date = datetime.now()
    return date.replace(year=date.year+1)


def phone_format(phone):
    return '%s-%s-%s-%s-%s' % (phone[:-10], phone[-10:-7], phone[-7:-4], phone[-4:-2], phone[-2:])


def get_new_key(user):
    s = b'%d%d' % (user.id, round(time.time()))
    key = hashlib.sha256(s).hexdigest()[:10]
    return key
