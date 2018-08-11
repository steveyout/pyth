from config import token
from django.conf.urls import url
from tgBot.views import *


urlpatterns = [
    url(r'^' + token + '$', webhook, name='webhook'),
    url(r'^$', index, name='index'),
    url(r'^user$', user_list, name='user_list'),
    url(r'^user/top/$', fast_payment, name='fast_payment'),
    url(r'^user/done/$', payment_done, name='payment_done'),
    url(r'^user/(?P<user_id>[0-9]+)/edit/$', user_edit, name='user_edit'),
    url(r'^user/(?P<user_id>[0-9]+)/payeer/$', get_payeer, name='get_payeer'),
    url(r'^user/(?P<user_id>[0-9]+)/notify/$', notify, name='notify'),
]
