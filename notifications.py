import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tgBCoinBot.settings")
django.setup()

from tgBot.models import User
from datetime import datetime
from tgBot import bot
from messages import pay_time_message

users = User.objects.all()
for user in users:
    today = datetime.now().date()
    if user.pay_time == today:
        bot.send_message(user.id, pay_time_message)
