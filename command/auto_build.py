#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# Create: 2021-11-24 17:31:26
# Author: huihui - sunjiehuimail@foxmail.com
# Filename: auto_build.py


import datetime
from flask_script import Command, Manager
from threading import Thread
from base import redis
from flask import current_app
from services.build_service import BuildLog


manager = Manager(description="build cmd")


class Consumer(Thread):
    """
    """
    def run(self):
        while True:
            task_info = redis.client.blpop("build_tasks", timeout=3600)
            if task_info:
                now = datetime.datetime.now()
                print(f"正在执行({str(now)}): {task_info}")
                try:
                    BuildLog.clone_build_project(*task_info[1].decode().split("|"))
                except Exception as e:
                    print(f"自动构建异常, {task_info} --- {str(e)}")
                print(f"执行结束({str(datetime.datetime.now())}): {task_info}")


class StartAutoBuild(Command):
    """
    开始自动构建消费
    """
    def run(self):
        print(">>: Start..")
        task_thread_num = current_app.config.get("TASK_THREAD_NUM", 1)

        for i in range(task_thread_num):
            c = Consumer()
            c.start()


class EndAutoBuild(Command):
    """
    结束自动构建消费
    """
    def run(self):
        print(">>: Undeveloped..")
        return

manager.add_command('start', StartAutoBuild())
manager.add_command('end', EndAutoBuild())
