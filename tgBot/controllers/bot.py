from telebot import types
from tgBot import bot
from tgBot.utils import to_main_page, to_invest_page, to_ref_page, to_pay_page, change_payeer
from tgBot.models import *
from tgBot.check import run as run_payment_check
from messages import before_pay_message, ref_message, invest_message, success_registration
from config import payeer_account

info_text = '''ХОЧЕШЬ ПОДНЯТЬСЯ С КОЛЕН, ПУТЕШЕСТВОВАТЬ И СМОТРЕТЬ НА БЫВШЕГО НАЧАЛЬНИКА ЕЩЁ БОЛЕЕ УНИЖАЮЩИМ ВЗГЛЯДОМ, ЧЕМ ОН СЕЙЧАС СМОТРИТ НА ТЕБЯ? ТОГДА ТЕБЕ, ДОЛЖНО БЫТЬ, ИЗВЕСТНО, ЧТО В последнее время появляется очень много позитивных новостей о криптовалюте, что способствует ее глобализации.🌎🌍🌏 Следовательно, благодаря этому, крипта стремительно растет и цена, и еще не поздно на этом разбогатеть и, наконец, создать себе те условия жизни, которые вы не можете себе позволить, работая на кого-то и тратя на это большую часть своего времени.😃 Основные функции бота SpiritualisMining – это 1) информирование о проекте, 2) сбор инвестиций, 3) постепенные выплаты денег, 4) также продвижение инициативы телеграмм канала «КРИПТОНИТ🎓». Создатели – опытные бойцы криптомира, благодаря своему опыту и знаниям, с легкостью имеют профит в 100% со своих инвестиций и абсолютно бесплатно делятся информацией. В скором времени добавится информация о баунти компаниях (это бесплатная раздача токинов), и если участвовать в них, то можно поднять тысячи долларов. 💰💰💰💰💰💰💰💰💰💰💰💰💰💰💰💰💰 Есть возможность заработать, рекламируя наш проект с помощью реферальной программы.👬👬👬👬👬 Если ты уже готов грести бабло, тогда начинай с нами! Боишься? Перед тем как максимально близко подошел к решающему действию, даешь заднюю? Тогда просто думай не о том, как будешь это делать, а думай, как будто уже сделал и добился положительного результата – тогда мозг не будет гудеть тревогу. И У ТЕБЯ ВСЕ ПОЛУЧИТСЯ!🏆🏆🏆'''

'''
    Here user is django user instance
'''


def existed_user_action(user, message):
    if user.state == 1:
        ask_for_refer(user, message)
    elif user.state == 2:
        wait_for_refer(user, message)
    elif user.state == 3:
        main_menu_action(user, message)
    elif user.state == 4:
        invest_page_action(user, message)
    elif user.state == 5:
        referal_page_action(user, message)
    elif user.state == 10:
        pay_in_action(user, message)
        return
    elif user.state == 20:
        remind_outcome_page(user, message)
    elif user.state == 40:
        payment_page_action(user, message)
    elif user.state == 41:
        wait_for_payeer(user, message)
    elif user.state == 30:
        if message.text == 'Инвестировать':
            user.dol_invested_sum += user.dol_accumulated_sum
            user.rub_invested_sum += user.rub_accumulated_sum
            user.rub_accumulated_sum = 0
            user.dol_accumulated_sum = 0
            to_main_page(user, 'Накопленная сумма успешно инвестирована')
        elif message.text == 'Назад':
            to_main_page(user)
    user.save()


def ask_for_refer(user, message):
    if message.text == 'Да':
        user.state = 2
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        back_button = types.KeyboardButton('Пропустить')
        markup.add(back_button)
        bot.send_message(user.id, 'Есть ли у вас ID пользователя-рефера? Без него вам будет выплаченно 115%', reply_markup=markup)
    elif message.text == 'Нет':
        user.state = 3
        to_main_page(user, success_registration)
    else:
        bot.send_message(user.id, 'Я понимаю только Да и Нет')


def wait_for_refer(user, message):
    if message.text == 'Пропустить':
        user.state = 3
        to_main_page(user, success_registration)
    else:
        try:
            ref_user = User.objects.filter(id=message.text).first()
        except Exception:
            bot.send_message(user.id, 'Невалидный ID')
            return
        if ref_user:
            if ref_user.id == user.id:
                bot.send_message(user.id, 'Вы не можете указать себя рефералом')
            else:
                user.ref_user = ref_user
                user.state = 3
                user.save()
                to_main_page(user, success_registration)
        else:
            bot.send_message(user.id, 'Пользователь с таким ID не найден! Попробуйте еще раз.')


def main_menu_action(user, message):
    if message.text == 'Информация о боте':
        bot.send_message(user.id, info_text)
    elif message.text == 'Инвестирование':
        user.state = 4
        to_invest_page(user, invest_message)
    elif message.text == 'Реферальная система':
        user.state = 5
        to_ref_page(user, ref_message)
    elif message.text == 'Выплаты':
        if user.payeer:
            user.state = 40
            to_pay_page(user, before_pay_message % user.payeer)
        else:
            change_payeer(user)


def invest_page_action(user, message):
    if message.text == 'Инвестировать':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        user.state = 10
        # new_key = get_new_key(user)
        # user.payment_key = new_key
        bot.send_message(user.id, user.id)
        pay = types.KeyboardButton('Оплатил')
        back = types.KeyboardButton('Назад')
        markup.add(pay, back)
        bot.send_message(user.id, '''Это ваш ключ для оплаты. Вставьте его в поле комментарий при оплате в системе payeer.
                                \n\n Средства перечислять на счет %s 
                                \n\nБольше информации на https://payeer.com/''' % payeer_account, reply_markup=markup)
    elif message.text == 'Инвестированная сумма':
        bot.send_message(user.id,
                         'Вы инвестировали %.2f рублей, %.2f долларов' % (user.rub_invested_sum, user.dol_invested_sum))
    elif message.text == 'Выплаченная сумма':
        bot.send_message(user.id,
                         'Вы получили %.2f рублей, %.2f долларов' % (user.rub_payed_outcome, user.dol_payed_outcome))
    elif message.text == 'Остаток по выплатам':
        # user.state = 20
        # markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        # markup.add(types.KeyboardButton('Реинвестировать'),
        #            types.KeyboardButton('Назад')
        #            )
        bot.send_message(user.id, 'Вы должны получить ещё %.2f рублей, %.2f долларов' % (
            user.rub_remind_outcome, user.dol_remind_outcome))
    elif message.text == 'Назад':
        to_main_page(user, '✅')


def referal_page_action(user, message):
    if message.text == 'Количество оплативших реералов':
        payed_refs = User.objects.filter(ref_user_id=user.id, have_payed=True).all()
        bot.send_message(user.id, 'Количество оплативших рефералов: %d чел.' % len(payed_refs))
    elif message.text == 'Накопленная сумма':
        user.state = 30
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton('Инвестировать'),
                   types.KeyboardButton('Назад'))
        bot.send_message(user.id, 'Накопленная Вами сумма: %.2f рублей, %.2f долларов' % (
            user.rub_accumulated_sum, user.dol_accumulated_sum), reply_markup=markup)
    elif message.text == 'ID для рефералов':
        bot.send_message(user.id, 'Ваш ID: %s' % str(user.id))
    elif message.text == 'Назад':
        to_main_page(user, '✅')


def pay_in_action(user, message):
    if message.text == 'Назад':
        to_main_page(user, '✅')
    elif message.text == 'Оплатил':
        bot.send_message(user.id, '''Мы запустили проверку. Если все верно, вы узнаете о результатах.
                                    \n\nЕсли вам ничего не пришло, проверьте верность платежа. Адрес назначения, секретный ключ, отсутствие секретной фразы.''')
        run_payment_check()


def remind_outcome_page(user, message):
    if message.text == 'Реинвестировать':
        user.dol_invested_sum += user.dol_remind_outcome
        user.rub_invested_sum += user.rub_remind_outcome
        user.dol_remind_outcome = 0
        user.rub_remind_outcome = 0
        to_main_page(user, 'Ваши накопления успешно реинвестированы')
    elif message.text == 'Назад':
        to_main_page(user)


def wait_for_payeer(user, message):
    if message.text == 'Назад':
        to_main_page(user)
    else:
        import re
        p = re.compile('P[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]$')
        res = p.match(message.text)
        if res:
            user.payeer = message.text
            to_main_page(user)
        else:
            bot.send_message(user.id,
                             'Это не является номером кошелька в системе Payeer.\n\n Более подробно на https://payeer.com')


def payment_page_action(user, message):
    # if message.text == 'Подтвердить':
    #     status = send_remind(user, message.text)
    #     if status == 0:
    #         message = 'Перевод был успешно выполнен'
    #     elif status == 1:
    #         message = 'В настоящий момент мы не можем перевести вам средства, зайдите в этот раздел позже'
    #     elif status == 2:
    #         message = 'Возникла ошибка при переводе рублей'
    #     elif status == 3:
    #         message = 'Возникла ошибка при переводе долларов'
    #     elif status == 4:
    #         message = 'Перевод не был выполнен. Мы делаем переводы от 1 рулбля и/или 0.01 доллара.'
    #     else:
    #         message = 'Возникла неизвестная ошибка, повторите попытку позже'
    #     to_main_page(user, message)
    if message.text == 'Изменить':
        change_payeer(user)
    elif message.text == 'Назад':
        to_main_page(user)
