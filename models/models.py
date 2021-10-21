#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# Create: 2021-10-08 17:05:07
# Author: huihui - sunjiehuimail@foxmail.com
# Filename: models.py


import datetime

from base import db
from utils import time_utils


WORK_TYPE = (
    (10, "后端"),
    (20, "前端"),
    (90, "其他"),
)


class GroupModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False, comment="组名")
    desc = db.Column(db.String(256), nullable=True, comment="简介")
    parent_id = db.Column(db.Integer, default=0, nullable=False, comment="父ID")
    email = db.Column(db.String(64), nullable=False, comment="邮箱")
    type_id = db.Column(db.Integer, nullable=True, comment="类型: 10 后端, 20 前端, 90 其他")
    is_deleted = db.Column(db.Boolean, default=False)
    dt_created = db.Column(db.DateTime, default=time_utils.now_dt)
    dt_updated = db.Column(db.DateTime, default=time_utils.now_dt, onupdate=time_utils.now_dt)

    def to_dict(self):
        ret_dict = {}
        for k in self.__table__.columns:
            value = getattr(self, k.name)
            if isinstance(value, datetime.datetime):
                value = value.strftime('%Y-%m-%d %H:%M:%S')
            elif k.name == "type_id":
                if not value:
                    ret_dict["type"] = dict()
                    continue
                type_dict = {
                    "id": value,
                    "name": dict(WORK_TYPE)[value]
                }
                ret_dict["type"] = type_dict
            ret_dict[k.name] = value
        return ret_dict


class DevUserModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False, comment="用户名")
    job = db.Column(db.String(64), nullable=False, comment="工作")
    desc = db.Column(db.String(256), nullable=True, comment="简介")
    # group_id = db.Column(db.Integer, nullable=False, comment="组ID")
    email = db.Column(db.String(64), nullable=False, comment="邮箱")
    is_deleted = db.Column(db.Boolean, default=False)
    dt_created = db.Column(db.DateTime, default=time_utils.now_dt)
    dt_updated = db.Column(db.DateTime, default=time_utils.now_dt, onupdate=time_utils.now_dt)


class UserGroupModel(db.Model):
    """
    用第3张表做多对多的关联, 既然后续都以组为纬度, 那肯定会有一个人多个组的可能
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False, comment="用户ID")
    group_id = db.Column(db.Integer, nullable=False, comment="组ID")
    is_deleted = db.Column(db.Boolean, default=False)
    dt_created = db.Column(db.DateTime, default=time_utils.now_dt)


class ProjectModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False, comment="项目名")
    desc = db.Column(db.String(256), nullable=True, comment="简介")
    ssh_url = db.Column(db.String(256), nullable=True, comment="SSL")
    http_url = db.Column(db.String(256), nullable=True, comment="HTTP")
    group_id = db.Column(db.Integer, nullable=False, comment="组ID(关联UserGroupModel)")
    type_id = db.Column(db.Integer, nullable=True, comment="类型: 10 后端,20 前端, 90 其他")
    is_deleted = db.Column(db.Boolean, default=False)
    dt_created = db.Column(db.DateTime, default=time_utils.now_dt)
    dt_updated = db.Column(db.DateTime, default=time_utils.now_dt, onupdate=time_utils.now_dt)


class BuildScriptModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    env = db.Column(db.String(12), nullable=True, comment="环境(感觉用不上枚举)")
    project_id = db.Column(db.Integer, nullable=False, comment="项目ID(关联ProjectModel)")
    script_path = db.Column(db.String(256), nullable=True, comment="脚本相对路径")
    archive_path = db.Column(db.String(256), nullable=True, comment="存档相对路径")
    script_type = db.Column(db.Integer, nullable=True, default=1, comment="脚本类型: 1 sh, 2 py")
    execute_comm = db.Column(db.Text, nullable=False, comment="执行命令")
    is_deleted = db.Column(db.Boolean, default=False)
    dt_created = db.Column(db.DateTime, default=time_utils.now_dt)
    dt_updated = db.Column(db.DateTime, default=time_utils.now_dt, onupdate=time_utils.now_dt)


class SubmitLogModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    version_num = db.Column(db.String(64), nullable=False, comment="版本号")
    title = db.Column(db.String(64), nullable=False, comment="标题")
    desc = db.Column(db.String(256), nullable=True, comment="描述")
    env = db.Column(db.String(12), nullable=False, comment="环境")
    project_id = db.Column(db.Integer, nullable=False, comment="项目ID(关联ProjectModel)")
    branch = db.Column(db.String(128), nullable=False, comment="分支")
    commit_hash = db.Column(db.String(128), nullable=True, comment="记录当时的最后commit号")
    status = db.Column(db.Integer, nullable=True, default=0, comment="状态: 0 未开始, 1 操作中, 2 成功, 3 失败")
    creator = db.Column(db.Integer, nullable=False, comment="创建人ID(关联DevUserModel)")
    is_deleted = db.Column(db.Boolean, default=False)
    dt_created = db.Column(db.DateTime, default=time_utils.now_dt)
    dt_updated = db.Column(db.DateTime, default=time_utils.now_dt, onupdate=time_utils.now_dt)


class BuildLogModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    version_num = db.Column(db.String(64), nullable=False, comment="版本号")
    title = db.Column(db.String(64), nullable=False, comment="标题")
    desc = db.Column(db.String(256), nullable=True, comment="描述")
    env = db.Column(db.String(12), nullable=False, comment="环境")
    project_id = db.Column(db.Integer, nullable=False, comment="项目ID(关联ProjectModel)")
    branch = db.Column(db.String(128), nullable=False, comment="分支")
    commit_hash = db.Column(db.String(128), nullable=True, comment="记录当时的最后commit号")
    status = db.Column(db.Integer, nullable=True, default=0, comment="状态: 0 未开始, 1 操作中, 2 成功, 3 失败")
    creator = db.Column(db.Integer, nullable=False, comment="创建人ID(关联DevUserModel)")
    build_type = db.Column(db.Integer, nullable=False, comment="类型: 1 手动, 2 自动")
    submit_id = db.Column(db.Integer, nullable=True, comment="提交ID(关联DevUserModel)")
    is_deleted = db.Column(db.Boolean, default=False)
    dt_created = db.Column(db.DateTime, default=time_utils.now_dt)
    dt_updated = db.Column(db.DateTime, default=time_utils.now_dt, onupdate=time_utils.now_dt)


class RequirementCodeModel(db.Model):
    """
    需求CODE
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False, comment="标题")
    code = db.Column(db.Integer, nullable=True, comment="状态码")
    is_deleted = db.Column(db.Boolean, default=False)
    dt_created = db.Column(db.DateTime, default=time_utils.now_dt)


class RequirementModel(db.Model):
    """
    需求表

    项目经理层
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False, comment="标题")
    desc = db.Column(db.String(256), nullable=True, comment="描述")
    status_code = db.Column(db.Integer, nullable=True, comment="状态(关联RequirementCodeModel)")
    delayed = db.Column(db.String(256), nullable=True, comment="过程记录")

    # plan
    dt_plan_started = db.Column(db.DateTime, nullable=False, default=time_utils.now_dt, comment="计划启动时间")
    dt_plan_deved = db.Column(db.DateTime, nullable=False, comment="计划开发时间")
    dt_plan_tested = db.Column(db.DateTime, nullable=False, comment="计划测试时间")
    dt_plan_released = db.Column(db.DateTime, nullable=False, comment="计划予发布时间")
    dt_plan_finished = db.Column(db.DateTime, nullable=False, comment="计划完成时间")

    # actual
    dt_started = db.Column(db.DateTime, nullable=True, comment="实际启动时间")
    dt_deved = db.Column(db.DateTime, nullable=True, comment="实际开发时间")
    dt_tested = db.Column(db.DateTime, nullable=True, comment="实际测试时间")
    dt_released = db.Column(db.DateTime, nullable=True, comment="实际予发布时间")
    dt_finished = db.Column(db.DateTime, nullable=True, comment="实际完成时间")

    is_deleted = db.Column(db.Boolean, default=False)
    dt_created = db.Column(db.DateTime, default=time_utils.now_dt)
    dt_updated = db.Column(db.DateTime, default=time_utils.now_dt, onupdate=time_utils.now_dt)


class RequirementProjectModel(db.Model):
    """
    需求/项目

    团队主管层
    需求跟项目关联, 有项目就会有组, 有组就能找到人, 需求的纬度对项目, 后续可对组(组可细划人)
    """
    id = db.Column(db.Integer, primary_key=True)
    requirement_id = db.Column(db.Integer, nullable=False, comment="需求ID(关联RequirementModel)")
    project_id = db.Column(db.Integer, nullable=False, comment="项目ID(关联ProjectModel)")
    group_id = db.Column(db.Integer, nullable=True, comment="组ID(关联GroupModel)")    # 可为空, 前期可以不使用
    branch = db.Column(db.String(128), nullable=False, comment="分支")
    progress_status = db.Column(db.Integer, nullable=False, comment="进度状态: 1 未开始, 2 进行中, 3 已完成, 4 事故中")
    requirement_status = db.Column(db.Integer, nullable=False, comment="需求状态: 1 未开始, 2 正常, 3 延期")
    dt_started = db.Column(db.DateTime, nullable=True, comment="开始时间")
    dt_finished = db.Column(db.DateTime, nullable=True, comment="完成时间")
    comment = db.Column(db.Text, nullable=False, comment="备注")
    is_deleted = db.Column(db.Boolean, default=False)
    dt_created = db.Column(db.DateTime, default=time_utils.now_dt)
    dt_updated = db.Column(db.DateTime, default=time_utils.now_dt, onupdate=time_utils.now_dt)
