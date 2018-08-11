from tgBot.models import User, Time
from config import *
import requests
import json
import datetime
from tgBot.utils import to_main_page
from tgBot.controllers.users import proceed_invest
from django.utils.timezone import pytz, now as timezone_now
from tgBCoinBot.settings import TIME_ZONE

tz = pytz.timezone(TIME_ZONE)


def get_json_data(begin, end):
    for i in range(0, 10):
        try:
            params = {
                'account': payeer_account,
                'apiId': payeer_api_id,
                'apiPass': payeer_api_pass,
                'action': 'history',
                'type': 'incoming',
                'from': begin.strftime('%Y-%m-%d %H:%M:%S'),
                'to': end.strftime('%Y-%m-%d %H:%M:%S'),
            }
            # headers = {
            #     'Content-Type': 'application/json'
            # }
            r = requests.post('https://payeer.com/ajax/api/api.php',
                              data=params)
            data = r.text
            data = json.loads(data)
            return data
        except Exception:
            pass


def run():
    try:
        now = timezone_now().astimezone(tz)
        check_time = Time.objects.filter(id=1).first()
        if not check_time:
            check_time = Time(time=now)
            previous_check = now - datetime.timedelta(days=10)
        else:
            previous_check = check_time.time.astimezone(tz)
        data = get_json_data(previous_check, now)
        errors = int(data['auth_error'])
        if errors != 0:
            raise Exception(data['errors'])
        else:
            history = data['history']
            if len(history):
                for key, operation in history.items():
                    if operation['to'] == payeer_account and operation['status'] == 'success':
                        user = User.objects.filter(id=operation['comment']).first()
                        if user:
                            amount = float(operation['creditedAmount'])
                            if operation['creditedCurrency'] == 'RUB':
                                currency = True
                            else:
                                currency = False
                            proceed_invest(user, amount, currency)
                            to_main_page(user,
                                         'Мы приняли вашу оплату %.2f %s в качестве бунуса даём вам ссылку на обучающий канал "Криптонит" https://t.me/cryptoparadise' % (
                                float(operation['creditedAmount']), operation['creditedCurrency']))
                            user.save()
            check_time.time = now
            check_time.save()
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(e)