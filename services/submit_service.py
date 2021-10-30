#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# Create: 2021-10-29 10:54:10
# Author: huihui - sunjiehuimail@foxmail.com
# Filename: services/submit_service.py


import time
import datetime

from base import db
from base.errors import ParamsError
from models.models import BuildLogModel
from .project_service import Project
from .user_service import User
from .gitlab_service import GitLab
from . import handle_page
from utils.time_utils import str2tsp


class Submit():
    """
    发布
    """
    @classmethod
    def list_submit(cls, keyword=None, user_id=None, type_id=None,
                   group_id=None, env=None, page_num=1, page_size=999):
        """
        发布列表

        keyword: 项目关键字筛选
        user_id: 操作人筛选
        type_id: 从产品方向是前后端的区分
        group_id: 组ID
        env_id: 环境CODE
        时间筛选待确定
        """
        log_obj_list = BuildLogModel.query.filter_by(is_deleted=False)
        if user_id:
            log_obj_list = log_obj_list.filter_by(creator=user_id)
        if type_id:
            log_obj_list = log_obj_list.filter_by(type_id=type_id)
        if env:
            log_obj_list = log_obj_list.filter_by(env=env)
        if group_id:
            log_obj_list = log_obj_list.filter_by(group_id=group_id)

        count = log_obj_list.count()
        log_obj_list = handle_page(log_obj_list, page_num, page_size)

        user_id_list = list()
        project_id_list = list()
        log_list = list()
        for i in log_obj_list:
            user_id_list.append(i.creator)
            project_id_list.append(i.project_id)
            log_list.append(i.to_dict())

        # 获取项目
        project_data = Project.list_project(id_list=project_id_list)

        project_dict_list = dict()
        for i in project_data["data_list"]:
            project_dict_list[i["id"]] = i

        # 获取用户
        user_data = User.list_user(user_id_list=user_id_list)
        user_dict_list = {
            0: {
                "id": 0,
                "name": "未知用户"
            }
        }
        for i in user_data["data_list"]:
            user_dict_list[i["id"]] = i

        for i in log_list:
            project_dict = project_dict_list.get(i["project_id"])
            if project_dict:
                i["name"] = project_dict["name"]
                i["desc"] = project_dict["desc"]
                i["duration"] = str2tsp(i["dt_updated"]) - str2tsp(i["dt_created"])
            else:
                i["name"] = ""
                i["desc"] = ""
                i["duration"] = 0

            user_dict = user_dict_list.get(i["creator"])
            if user_dict:
                i["operator"] = user_dict
            else:
                i["operator"] = user_dict_list[0]
        ret = {
            "data_list": log_list,
            "count": count
        }

        return ret

    @classmethod
    def add_submit(cls, log_id):
        return
