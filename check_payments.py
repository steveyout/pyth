import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tgBCoinBot.settings")
django.setup()

from tgBot.check import run


if __name__ == '__main__':
    run()
