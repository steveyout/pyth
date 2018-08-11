from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
import json
import telebot
from . import bot
from .handlers import *
from .controllers.users import edit_user
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from tgBot.utils import change_payeer


# Create your views here.


def webhook(request):
    data = json.loads(request.body.decode('utf-8'))
    update = telebot.types.Update.de_json(data)
    bot.process_new_updates([update])

    return HttpResponse(content="Ok", status=200)


@login_required(login_url='login')
def index(request):
    return redirect('user_list')


@login_required(login_url='login')
def user_list(request):
    users = User.objects
    if 'id' in request.GET:
        try:
            user_id = int(request.GET['id'])
            users = users.filter(id=user_id)
        except:
            pass
    users = users.all()
    return render(request, 'user_list.html', context={'users': users})


@login_required(login_url='login')
def fast_payment(request):
    users = User.objects.filter(Q(rub_invested_sum__gte=10000)|Q(dol_invested_sum__gte=300))
    if 'id' in request.GET:
        try:
            user_id = int(request.GET['id'])
            users = users.filter(id=user_id)
        except:
            pass
    users = users.all()
    return render(request, 'user_list.html', context={'users': users})


@login_required(login_url='login')
def payment_done(request):
    users = User.objects.filter(Q(rub_remind_outcome=0), Q(dol_remind_outcome=0))
    if 'id' in request.GET:
        try:
            user_id = int(request.GET['id'])
            users = users.filter(id=user_id)
        except:
            pass
    users = users.all()
    return render(request, 'user_list.html', context={'users': users})


@login_required(login_url='login')
def user_edit(request, user_id):
    user = get_object_or_404(User, id=user_id)
    message = None
    if request.method == 'POST':
        status, message = edit_user(user, request.POST)
        if status:
            return redirect('user_list')
    return render(request, 'user_edit.html', context={'user': user, 'error': message})


@login_required(login_url='login')
def get_payeer(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.state = 41
    change_payeer(user)
    user.save()
    return redirect('user_list')


@login_required(login_url='login')
def notify(request, user_id):
    user = get_object_or_404(User, id=user_id)
    bot.send_message(user.id, 'Вам были осуществлены выплаты, проверьте ваш кошелек на https://payeer.com/')
    return redirect('user_list')
