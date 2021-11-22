#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# Create: 2021-10-29 10:54:10
# Author: huihui - sunjiehuimail@foxmail.com
# Filename: services/submit_service.py


import datetime

from base import db
from base.errors import ParamsError
from models.models import BuildLogModel, SubmitLogModel
from .project_service import Project
from .user_service import User
from .gitlab_service import GitLab
from .deploy_service import Deploy
from . import handle_page
from utils.time_utils import str2tsp
from utils import async_func


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
        log_obj_list = SubmitLogModel.query.filter_by(is_deleted=False) \
            .order_by(SubmitLogModel.id.desc())
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
        if not log_list:
            ret = {
                "data_list": list(),
                "count": 0
            }

            return ret

        # 获取项目
        project_data = Project.list_project(id_list=project_id_list,
                                            need_git_info=False)

        project_dict_list = dict()
        for i in project_data["data_list"]:
            project_dict_list[i["id"]] = i

        # 获取用户
        user_data = User.list_user(user_id_list=user_id_list)
        user_dict_list = {
            0: {
                "id": 0,
                "name": "未知"
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
    def add_submit(cls, log_id, user_id=0):
        try:
            build_obj = BuildLogModel.query.get(log_id)
        except Exception as e:
            raise ParamsError("交付失败, 制品ID错误或已被删除")

        s_params = {
            "version_num": build_obj.version_num,
            "title": build_obj.title,
            "desc": build_obj.desc,
            "env": build_obj.env,
            "project_id": build_obj.project_id,
            "branch": build_obj.branch,
            "commit_hash": build_obj.commit_hash,
            "status": 1,
            "creator": user_id,
            "build_type": build_obj.build_type,
            "file_path": build_obj.file_path,
            "submit_id": build_obj.submit_id,
            "group_id": build_obj.group_id,
            "type_id": build_obj.type_id,
            "dt_build": build_obj.dt_created,
        }

        submit_log_obj = SubmitLogModel(**s_params)
        db.session.add(submit_log_obj)
        db.session.commit()

        return submit_log_obj.to_dict()

    @classmethod
    def update_status(cls, id, status_id):
        submit_obj = SubmitLogModel.query.get(id)
        submit_obj.status = status_id
        db.session.commit()
        return

    @classmethod
    @async_func
    def async_add_deploy(cls, submit_id, project_id, file_path, env):
        """
        TODO log
        """
        try:
            from application import app
            with app.app_context():
                ret = Deploy.add_deploy(project_id, file_path, env)
                if ret:
                    cls.update_status(submit_id, 3)
                    print(f"Deploy Error, {ret}")
                    return

                cls.update_status(submit_id, 2)
        except Exception as e:
            print(f">> Deploy Error, {str(e)}")
            cls.update_status(submit_id, 3)
        return

    @classmethod
    def query_submit(cls, id):
        try:
            submit_obj = SubmitLogModel.query.get(id)
        except:
            raise ParamsError("日志记录异常")

        ret = submit_obj.to_dict()
        return ret
