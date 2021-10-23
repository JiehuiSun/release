#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# Create: 2021-10-23 16:43:19
# Author: huihui - sunjiehuimail@foxmail.com
# Filename: services/build_service.py


from base import db
from base.errors import ParamsError
from models.models import BuildLogModel
from .project_service import Project
from .user_service import User


class Build():
    """
    制品
    """
    @classmethod
    def list_build(cls, keyword=None, user_id=None, type_id=None,
                   group_id=None, env_id=None):
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

        build_obj_list = BuildLogModel.query.filter_by(is_deleted=False)
        build_obj_list = build_obj_list.filter(BuildLogModel.project_id.in_(project_id_list))

        if user_id:
            build_obj_list = build_obj_list.filter_by(creator=user_id)
        if env_id:
            # TODO 库里直接使用环境名还是使用枚举?
            build_obj_list = build_obj_list.filter_by(env=env_id)

        # TODO 正常只取以project_id分组的最新一条即可
        build_obj_list = build_obj_list.all()

        build_dict_list = dict()
        need_user_id_list = list()
        for i in build_obj_list:
            if build_dict_list:
                continue

            build_dict = {
                "version_num": i.version_num,
                "creator": i.creator,
                "last_status": i.status,
                "dt_last_submit": i.dt_created,
                "last_duration": (i.dt_updated - i.dt_created).seconds
            }
            build_dict_list[i.project_id] = build_dict
            need_user_id_list.append(build_dict["creator"])

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
            build_dict = build_dict_list.get(i["id"])
            if build_dict:
                i.update(build_dict)
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
