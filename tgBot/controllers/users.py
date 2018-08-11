from tgBot.models import *
from telebot import types
from tgBot import bot
from datetime import datetime
from config import payeer_account, payeer_api_pass, payeer_api_id
import requests
import json
from messages import hello_message

'''
    Here user is telebot instance of user
'''


# info_text = 'Приветствуем Вас! В данном чат-боте Вы можете инвестировать свои средства в криптовалюту и получать до 10% годовых.'


def get_user(user):
    result = User.objects.filter(id=user.id).first()
    if result is None:
        result = _create_user(user)
        return False, result
    else:
        return True, result


def _create_user(telegram_user):
    user = User(id=telegram_user.id)
    user.save()
    # TODO make getting message from file or db

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    phone_button = types.KeyboardButton('Отправить номер телефона', request_contact=True)
    markup.add(phone_button)

    bot.send_message(user.id, hello_message, reply_markup=markup)
    return user


def proceed_invest(user, input_sum, currency):
    if currency:
        user.rub_invested_sum += input_sum
        if user.ref_user:
            user.ref_user.rub_accumulated_sum += input_sum * 0.05
    else:
        user.dol_invested_sum += input_sum
        if user.ref_user:
            user.ref_user.dol_accumulated_sum += input_sum * 0.05
    user.payment_key = None
    user.have_payed = True
    user.save()
    if user.ref_user:
        user.ref_user.save()


def edit_user(user, post_dict):
    print(post_dict)
    message = ''
    error = False
    if 'ref_user' in post_dict:
        ref_user = post_dict['ref_user']
        if ref_user is not '':
            try:
                user.ref_user_id = User.objects.get(id=ref_user)
            except:
                error = True
                message += 'No such refer user\n'
        else:
            user.ref_user = None
    if 'pay_time' in post_dict:
        try:
            user.pay_time = datetime.strptime(post_dict['pay_time'], "%Y-%m-%d").date()
        except ValueError:
            error = True
            message = 'Invalid value for date\n'
    if 'invested_rub' in post_dict:
        try:
            user.rub_invested_sum = float(post_dict['invested_rub'])
        except ValueError:
            error = True
            message += 'Invalid value for invested rub sum \n'
    if 'invested_dol' in post_dict:
        try:
            user.dol_invested_sum = float(post_dict['invested_dol'])
        except ValueError:
            error = True
            message += 'Invalid value for invested_dol sum \n'
    if 'accumulated_rub' in post_dict:
        try:
            user.rub_accumulated_sum = float(post_dict['accumulated_rub'])
        except ValueError:
            error = True
            message += 'Invalid value for accumulated_rub sum \n'
    if 'accumulated_dol' in post_dict:
        try:
            user.dol_accumulated_sum = float(post_dict['accumulated_dol'])
        except ValueError:
            error = True
            message += 'Invalid value for accumulated_dol sum \n'
    if 'payed_rub' in post_dict:
        try:
            user.rub_payed_outcome = float(post_dict['payed_rub'])
        except ValueError:
            error = True
            message += 'Invalid value for payed_rub sum \n'
    if 'payed_dol' in post_dict:
        try:
            user.dol_payed_outcome = float(post_dict['payed_dol'])
        except ValueError:
            error = True
            message += 'Invalid value for payed_dol sum \n'
    if 'remind_rub' in post_dict:
        try:
            user.rub_remind_outcome = float(post_dict['remind_rub'])
        except ValueError:
            error = True
            message += 'Invalid value for remind_rub sum \n'
    if 'remind_dol' in post_dict:
        try:
            user.dol_remind_outcome = float(post_dict['remind_dol'])
        except ValueError:
            error = True
            message += 'Invalid value for remind_dol sum \n'
    if 'payeer' in post_dict:
        try:
            payeer = post_dict['remind_dol']
            if payeer != '':
                import re
                p = re.compile('P[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]$')
                res = p.match(payeer)
                if res:
                    user.payeer = payeer
                else:
                    error = True
                    message += 'Wrong value for payeer'
        except ValueError:
            error = True
            message += 'Invalid value for remind_dol sum \n'

    if error:
        return None, message
    else:
        user.save()
        return user, message


def send_remind(user, payeer):
    params = {
        'account': payeer_account,
        'apiId': payeer_api_id,
        'apiPass': payeer_api_pass,
        'action': 'balance',
    }
    r = requests.post('https://payeer.com/ajax/api/api.php',
                      data=params)
    data = r.text
    data = json.loads(data)
    if data['errors']:
        return 5
    else:
        have_usd = float(data['balance']['USD']['DOSTUPNO_SYST'])
        have_rub = float(data['balance']['RUB']['DOSTUPNO_SYST'])
        if have_rub >= user.rub_remind_outcome and have_usd >= user.dol_remind_outcome:
            if user.rub_remind_outcome >= 1:
                params = {
                    'account': payeer_account,
                    'apiId': payeer_api_id,
                    'apiPass': payeer_api_pass,
                    'action': 'transfer',
                    'curIn': 'RUB',
                    'sum': user.rub_remind_outcome,
                    'curOut': 'RUB',
                    'to': payeer
                }
                r = requests.post('https://payeer.com/ajax/api/api.php',
                                  data=params)
                data = r.text
                data = json.loads(data)
                if data['errors']:
                    return 2
                user.rub_payed_outcome += user.rub_remind_outcome
                user.rub_remind_outcome = 0
            else:
                return 4
            if user.dol_remind_outcome >= 0.02:
                params = {
                    'account': payeer_account,
                    'apiId': payeer_api_id,
                    'apiPass': payeer_api_pass,
                    'action': 'transfer',
                    'curIn': 'USD',
                    'sum': user.dol_remind_outcome,
                    'curOut': 'USD',
                    'to': payeer
                }
                r = requests.post('https://payeer.com/ajax/api/api.php',
                                  data=params)
                data = r.text
                data = json.loads(data)
                if data['errors']:
                    return 3
                user.dol_payed_outcome += user.dol_remind_outcome
                user.dol_remind_outcome = 0
            else:
                return 4
            return 0
        else:
            return 1
