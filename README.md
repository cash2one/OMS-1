# OMS
orders manage system

#start a worker instance by using the celery worker manage command
Celery worker:$ celery -A oms worker -l info
Celery scheduler:$ celery -A oms beat -l info -S django		#--scheduler django_celery_beat.schedulers:DatabaseScheduler
