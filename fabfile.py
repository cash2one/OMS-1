# -*- coding: utf-8 -*-
from fabric.api import env, local, cd, run


def staging():
    """ 设置 staging 环境 """
    env.hosts = ["root@47.95.235.167"]
    env.password = "xbm201512"


def prepare():
    """ 本地提交代码，准备部署 """
    local("git pull")
    # local("pip freeze > requirements.txt")
    local("git add . && git commit -m '自动部署提交'")
    local("git push")


def update():
    """ 服务器上更新代码、依赖和迁移 """
    # TODO 虚拟环境 依赖 数据库迁移
    with cd("/home/workspace/OMS"):
        run("git pull")
        # run("pip install -r requirements.txt")
        # run("python3 manage.py makemigrations && python3 manage.py migrate")
        # run("celery -A oms_server worker -l info")
        run("supervisorctl restart oms")


def deploy():
    prepare()
    update()
