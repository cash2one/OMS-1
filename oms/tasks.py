# coding:utf-8
# from celery.decorators import task
from oms.custom_celery import app
import time
from oms.models.order import Order


@app.task
def sendmail(email):
    time.sleep(2)
    print("============================================")
    print('start send email to %s' % email)
    orders = Order.objects.all()
    print(len(orders))
    time.sleep(5)  # 休息5秒
    print('success')
    return True
