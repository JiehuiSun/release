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
from .gitlab_service import GitLab
from . import handle_page, gen_version_num
from utils.time_utils import str2tsp, datetime_2_str_by_format


class Build():
    """
    制品
    """
    @classmethod
    def list_build(cls, keyword=None, user_id=None, type_id=None,
                   group_id=None, env=None, page_num=1, page_size=999):
        """
        制品库列表

        keyword: 项目关键字筛选
        user_id: 操作人筛选
        type_id: 从产品方向是前后端的区分
        group_id: 组ID
        env_id: 环境CODE
        时间筛选待确定
        """
        project_params = {
            "page_num": page_num,
            "page_size": page_size,
            "is_base": True,
        }
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
        if env:
            # TODO 库里直接使用环境名还是使用枚举?
            build_obj_list = build_obj_list.filter_by(env=env)

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
                "dt_last_submit": datetime_2_str_by_format(i.dt_created),
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


class BuildLog():
    """
    制品日志
    """
    @classmethod
    def list_build_log(cls, project_id, status_id=None, env=None,
                       page_num=1, page_size=999):
        log_obj_list = BuildLogModel.query.filter_by(project_id=project_id,
                                                     is_deleted=False).order_by(BuildLogModel.id.desc())
        if status_id:
            log_obj_list = log_obj_list.filter_by(status=status_id)
        if env:
            log_obj_list = log_obj_list.filter_by(env=env)

        count = log_obj_list.count()
        log_obj_list = handle_page(log_obj_list, page_num, page_size)

        log_list = list()
        user_id_list = list()
        for i in log_obj_list:
            log_dict = i.to_dict()
            user_id_list.append(log_dict["creator"])
            log_list.append(log_dict)

        user_data = User.list_user(user_id_list=user_id_list)
        user_dict_list = dict()
        for i in user_data["data_list"]:
            if i["id"] in user_dict_list:
                continue
            user_dict_list[i["id"]] = {
                "id": i["id"],
                "name": i["name"]
            }

        for i in log_list:
            user_dict = user_dict_list.get(i["creator"])
            if not user_dict:
                user_dict = {
                    "id": 0,
                    "name": "未知用户"
                }
            i["operator"] = user_dict

            i["duration"] = str2tsp(i["dt_updated"]) - str2tsp(i["dt_created"])
            i["fetch_duration"] = str2tsp(i["dt_updated"]) - str2tsp(i["dt_created"])

        ret = {
            "data_list": log_list,
            "count": count
        }

        return ret

    @classmethod
    def add_build_log(cls, project_id, branch, env, commit_id=None):
        project_dict = Project.query_project(project_id, False)

        source_project_id = project_dict["source_project_id"]
        http_url = project_dict["http_url"]
        name = project_dict["name"]

        name = name.replace(" ", "_")
        log_count = BuildLogModel.query.filter_by(project_id=project_id,
                                                  branch=branch).count()
        tar_file_name = gen_version_num(name, log_count+1, env, branch)

        build_log_dict = {
            "version_num": tar_file_name,
            "title": f"#{log_count+1}_【{branch}】",
            "env": env,
            "project_id": project_id,
            "branch": branch,
            "commit_hash": commit_id,
            "status": 1, # TODO
            "creator": 0, # TODO
            "build_type": 1,
            "type_id": project_dict["type_id"],
            "group_id": project_dict["group_id"],
        }
        build_obj = BuildLogModel(**build_log_dict)
        db.session.add(build_obj)
        db.session.commit()

        try:
            tar_file_dict = GitLab.clone_project(name, tar_file_name, source_project_id, branch)
        except Exception as e:
            build_obj.status = 3
            db.session.commit()
            raise ParamsError(f"Build Err! Clone Err {str(e)}")

        build_obj.status = 2
        build_obj.file_path = tar_file_dict["path"]
        db.session.commit()

        return
