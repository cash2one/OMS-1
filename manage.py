#!/usr/bin/env python
import os
import sys
# from oms.services.task_service import settle_storge_cost
# from oms.services.scheduler_service import scheduler
# from oms.services.task_service import settle_storge_cost


if __name__ == "__main__":
    env = os.environ.get("AIRCOS_ENV", "test")
    print("xxxxxxxxxxxxxxxxxxxxxxx")
    print(env)
    if env == "product":
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "oms.settings.product")
    elif env == "test":
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "oms.settings.test")
    else:
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "oms.settings.local")

    from django.core.management import execute_from_command_line
    # scheduler.add_job(settle_storge_cost, 'cron', hour='14')
    # scheduler.start()
    # from oms_server.tasks import setup_periodic_tasks
    # setup_periodic_tasks()
    execute_from_command_line(sys.argv)
