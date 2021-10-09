#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# Create: 2021-10-08 17:05:07
# Author: huihui - sunjiehuimail@foxmail.com
# Filename: models.py


from base import db
from utils import time_utils


class GroupModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False, comment="用户名")
    desc = db.Column(db.String(256), nullable=True, comment="简介")
    parent_id = db.Column(db.Integer, default=0, nullable=False, comment="父ID")
    email = db.Column(db.String(64), nullable=False, comment="邮箱")
    is_deleted = db.Column(db.Boolean, default=False)
    dt_create = db.Column(db.DateTime, default=time_utils.now_dt)
    dt_update = db.Column(db.DateTime, default=time_utils.now_dt, onupdate=time_utils.now_dt)


class UserModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False, comment="用户名")
    job = db.Column(db.String(64), nullable=False, comment="工作")
    desc = db.Column(db.String(256), nullable=True, comment="简介")
    # group_id = db.Column(db.Integer, nullable=False, comment="组ID")
    email = db.Column(db.String(64), nullable=False, comment="邮箱")
    is_deleted = db.Column(db.Boolean, default=False)
    dt_create = db.Column(db.DateTime, default=time_utils.now_dt)
    dt_update = db.Column(db.DateTime, default=time_utils.now_dt, onupdate=time_utils.now_dt)


class UserGroupModel(db.Model):
    """
    用第3张表做多对多的关联, 既然后续都以组为纬度, 那肯定会有一个人多个组的可能
    """
    user_id = db.Column(db.Integer, nullable=False, comment="用户ID")
    group_id = db.Column(db.Integer, nullable=False, comment="组ID")
    is_deleted = db.Column(db.Boolean, default=False)
    dt_create = db.Column(db.DateTime, default=time_utils.now_dt)


class ProjectModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False, comment="用户名")
    desc = db.Column(db.String(256), nullable=True, comment="简介")
    ssh_url = db.Column(db.String(256), nullable=True, comment="SSL")
    http_url = db.Column(db.String(256), nullable=True, comment="HTTP")
    group_id = db.Column(db.Integer, nullable=False, comment="组ID(从UserGroupModel中找)")
    is_deleted = db.Column(db.Boolean, default=False)
    dt_create = db.Column(db.DateTime, default=time_utils.now_dt)
    dt_update = db.Column(db.DateTime, default=time_utils.now_dt, onupdate=time_utils.now_dt)


class BuildScriptModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    env = db.Column(db.String(12), nullable=True, comment="环境(感觉用不上枚举)")
    script_path = db.Column(db.String(256), nullable=True, comment="脚本相对路径")
    archive_path = db.Column(db.String(256), nullable=True, comment="存档相对路径")
    script_type = db.Column(db.Integer, nullable=True, default=1, comment="脚本类型: 1 sh, 2 py")
    execute_comm = db.Column(db.Text, nullable=False, comment="执行命令")
    is_deleted = db.Column(db.Boolean, default=False)
    dt_create = db.Column(db.DateTime, default=time_utils.now_dt)
    dt_update = db.Column(db.DateTime, default=time_utils.now_dt, onupdate=time_utils.now_dt)
