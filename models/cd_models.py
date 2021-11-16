#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# Create: 2021-11-13 18:28:27
# Author: huihui - sunjiehuimail@foxmail.com
# Filename: cd_models.py


import datetime

from base import db
from utils import time_utils


class Hosts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False, comment="名称")
    # zone = db.Column(db.String(64), nullable=True, comment="zone") # tmp
    is_verified = db.Column(db.Boolean, default=True) # tmp
    hostname = db.Column(db.String(64), nullable=False, comment="主机名")
    port = db.Column(db.Integer, nullable=False, default=22, comment="端口")
    username = db.Column(db.String(64), nullable=False, comment="用户名")
    pkey = db.Column(db.Text, nullable=True, comment="私钥")
    desc = db.Column(db.String(256), nullable=False, comment="简介")
    created_at = db.Column(db.DateTime, default=time_utils.now_dt)
    created_by_id = db.Column(db.Integer, nullable=True, comment="创建者ID")

    def to_dict(self):
        ret_dict = {}
        for k in self.__table__.columns:
            if k.name == "is_deleted":
                continue
            value = getattr(self, k.name)
            if isinstance(value, datetime.datetime):
                value = value.strftime('%Y-%m-%d %H:%M:%S')
            ret_dict[k.name] = value
        return ret_dict


class HostProject(db.Model):
    """
    TODO 增加字段
    项目在服务器上的目录
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False, comment="名称")
    host_id = db.Column(db.Integer, nullable=True, comment="创建者ID")
    project_id = db.Column(db.Integer, nullable=True, comment="创建者ID")
    path = db.Column(db.String(256), nullable=False, comment="服务目录")
    ignore_text = db.Column(db.Text, nullable=True, comment="忽略文件(一行一个文件, 相对路径)")
    env = db.Column(db.String(24), nullable=True, comment="环境")
    is_deleted = db.Column(db.Boolean, default=False)
    dt_created = db.Column(db.DateTime, default=time_utils.now_dt)
    dt_updated = db.Column(db.DateTime, default=time_utils.now_dt, onupdate=time_utils.now_dt)
