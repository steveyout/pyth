from django.db import models
from .utils import year_from_now
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
# Create your models here.


'''
States of user:
0 is just came user, we have to know his telephone number
1 we know his phone number, we want to ask him about refferal
2 we are waiting for refferal id
3 user is fully registered
'''


class User(models.Model):
    id = models.IntegerField(primary_key=True)
    phone = models.CharField(null=True, max_length=40)
    ref_user = models.ForeignKey('User', null=True)
    state = models.IntegerField(default=0)
    rub_invested_sum = models.FloatField(default=0)
    dol_invested_sum = models.FloatField(default=0)
    rub_accumulated_sum = models.FloatField(default=0)
    dol_accumulated_sum = models.FloatField(default=0)
    rub_payed_outcome = models.FloatField(default=0)
    dol_payed_outcome = models.FloatField(default=0)

    rub_remind_outcome = models.FloatField(default=0)
    dol_remind_outcome = models.FloatField(default=0)

    have_payed = models.BooleanField(default=False)
    pay_time = models.DateField(default=year_from_now)
    payeer = models.CharField(null=True, max_length=10)


class Time(models.Model):
    time = models.DateTimeField()


@receiver(pre_save, sender=User)
def user_pre_save(sender, **kwargs):
    kwargs['instance'].rub_invested_sum = round(kwargs['instance'].rub_invested_sum, 2)
    kwargs['instance'].dol_invested_sum = round(kwargs['instance'].dol_invested_sum, 2)

    kwargs['instance'].rub_accumulated_sum = round(kwargs['instance'].rub_accumulated_sum, 2)
    kwargs['instance'].dol_accumulated_sum = round(kwargs['instance'].dol_accumulated_sum, 2)

    kwargs['instance'].rub_payed_outcome = round(kwargs['instance'].rub_payed_outcome, 2)
    kwargs['instance'].dol_payed_outcome = round(kwargs['instance'].dol_payed_outcome, 2)

    kwargs['instance'].rub_remind_outcome = round(kwargs['instance'].rub_remind_outcome, 2)
    kwargs['instance'].dol_remind_outcome = round(kwargs['instance'].dol_remind_outcome, 2)

