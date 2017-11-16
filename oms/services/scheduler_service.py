# import logging
# from apscheduler.schedulers.background import BackgroundScheduler
# from apscheduler.jobstores.redis import RedisJobStore
# from apscheduler.executors.pool import ThreadPoolExecutor
# from apscheduler.executors.pool import ProcessPoolExecutor


# log = logging.getLogger('apscheduler.executors.default')
# log.setLevel(logging.DEBUG)  # DEBUG
# # 设定日志格式
# fmt = logging.Formatter('%(levelname)s:%(name)s:%(message)s')
# h = logging.StreamHandler()
# h.setFormatter(fmt)
# log.addHandler(h)


# jobstores = {
#     'default': RedisJobStore(host='127.0.0.1', port=6379, db=0)
# }
# executors = {
#     'default': ThreadPoolExecutor(20),
#     'processpool': ProcessPoolExecutor(4)
# }
# job_defaults = {
#     'coalesce': True,
#     'max_instances': 3
# }


# scheduler = BackgroundScheduler(
#   jobstores=jobstores,
#   executors=executors,
#   job_defaults=job_defaults
# )
