#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# Create: 2021-10-29 10:54:10
# Author: huihui - sunjiehuimail@foxmail.com
# Filename: services/submit_service.py


import time
import datetime

from base import db
from base.errors import ParamsError
from models.models import SubmitLogModel
from .project_service import Project
from .user_service import User
from .gitlab_service import GitLab


class Submit():
    """
    制品
    """
    @classmethod
    def list_submit(cls, keyword=None, user_id=None, type_id=None,
                   group_id=None, env=None):
        """
        制品库列表

        keyword: 项目关键字筛选
        user_id: 操作人筛选
        type_id: 从产品方向是前后端的区分
        group_id: 组ID
        env_id: 环境CODE
        时间筛选待确定
        """
        project_params = dict()
        if keyword:
            project_params["keyword"] = keyword
        if group_id:
            project_params["group_id"] = group_id
        if type_id:
            project_params["type_id"] = type_id

        project_data = Project.list_project(**project_params)
        project_list = project_data["data_list"]
        project_id_list = [i["id"] for i in project_list]

        if not project_id_list:
            ret = {
                "data_list": list(),
                "count": 0
            }
            return ret

        submit_obj_list = SubmitLogModel.query.filter_by(is_deleted=False)
        submit_obj_list = submit_obj_list.filter(SubmitLogModel.project_id.in_(project_id_list))

        if user_id:
            submit_obj_list = submit_obj_list.filter_by(creator=user_id)
        if env:
            # TODO 库里直接使用环境名还是使用枚举?
            submit_obj_list = submit_obj_list.filter_by(env=env)

        # TODO 正常只取以project_id分组的最新一条即可
        submit_obj_list = submit_obj_list.all()

        submit_dict_list = dict()
        need_user_id_list = list()
        for i in submit_obj_list:
            if submit_dict_list:
                continue

            submit_dict = {
                "version_num": i.version_num,
                "creator": i.creator,
                "last_status": i.status,
                "dt_last_submit": i.dt_created,
                "last_duration": (i.dt_updated - i.dt_created).seconds
            }
            submit_dict_list[i.project_id] = submit_dict
            need_user_id_list.append(submit_dict["creator"])

        # 一次性获取用户
        user_data = User.list_user(user_id_list=need_user_id_list)
        user_dict_list = dict()
        for i in user_data["data_list"]:
            if i["id"] in user_dict_list:
                continue
            user_dict_list[i["id"]] = {
                "id": i["id"],
                "name": i["name"]
            }

        # 整合数据
        for i in project_list:
            submit_dict = submit_dict_list.get(i["id"])
            if submit_dict:
                i.update(submit_dict)
            else:
                i["last_status"] = dict()
                i["dt_last_submit"] = ""
                i["last_duration"] = 0
                i["creator"] = 0
                i["version_num"] = ""

            if i["creator"]:
                user_dict = user_dict_list.get(i["creator"])
                if user_dict:
                    i["operator"] = user_dict
                    continue

            # 用户不存在或已被删除
            i["operator"] = {
                "id": 0,
                "name": "未知用户"
            }

        ret = {
            "data_list": project_list,
            "count": project_data["count"]
        }
        return ret


class SubmitLog():
    """
    制品日志
    """
    @classmethod
    def list_submit_log(cls, project_id, status_id=None, env=None):
        log_obj_list = SubmitLogModel.query.filter_by(project_id=project_id,
                                                     is_deleted=False)
        if status_id:
            log_obj_list = log_obj_list.filter_by(status=status_id)
        if env:
            log_obj_list = log_obj_list.filter_by(env=env)

        count = log_obj_list.count()
        log_obj_list = log_obj_list.all()

        log_list = list()
        for i in log_obj_list:
            log_dict = i.to_dict()
            log_dict["operator"] = {
                "id": 1,
                "name": "狗子"
            }
            log_list.append(log_dict)

        ret = {
            "data_list": log_list,
            "count": count
        }

        return ret

    @classmethod
    def add_submit_log(cls, project_id, branch, env, commit_id=None):
        project_dict = Project.query_project(project_id, False)

        source_project_id = project_dict["source_project_id"]
        http_url = project_dict["http_url"]
        name = project_dict["name"]

        name = name.replace(" ", "_")
        tar_file_name = f"{name}_{str(datetime.datetime.now()).split()[0]}_{str(int(time.time()))[5:]}"

        submit_log_dict = {
            "version_num": tar_file_name,
            "title": f"{name} Submit",
            "env": env,
            "project_id": project_id,
            "branch": branch,
            "commit_hash": commit_id,
            "status": 1, # TODO
            "creator": 0, # TODO
            "submit_type": 1
        }
        submit_obj = SubmitLogModel(**submit_log_dict)
        db.session.add(submit_obj)
        db.session.commit()

        try:
            tar_file_dict = GitLab.clone_project(name, tar_file_name, source_project_id, branch)
        except Exception as e:
            submit_obj.status = 3
            db.session.commit()
            raise ParamsError(f"Submit Err! Clone Err {str(e)}")

        submit_obj.status = 2
        submit_obj.file_path = tar_file_dict["path"]
        db.session.commit()

        return
