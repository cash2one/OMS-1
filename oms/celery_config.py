BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['application/json', ]
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Shanghai'
# CELERY_TIMEZONE = 'Europe/London'
from celery.schedules import crontab
CELERY_ENABLE_UTC = True
# CELERYBEAT_SCHEDULE = {
#     'storge_billing_every_day_0_hour': {
#         'task': 'oms_server.tasks.storge_billing',
#         'schedule': crontab(hour=10, minute=4),
#         'args': ()
    # },
    # 'overdue_billing_every_month_first_day': {
    #     'task': 'oms_server.tasks.overdue_billing',
    #     'schedule': crontab(minute='0', hour='0', day_of_month='1'),
    #     'args': ()
    # },
    # 'refresh_token_every_3_hour': {
    #     'task': 'oms_server.tasks.refresh_token',
    #     'schedule': datetime.timedelta(hours=3),
    #     'args': ()
    # },
# }