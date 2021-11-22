#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# Create: 2021-10-23 16:43:19
# Author: huihui - sunjiehuimail@foxmail.com
# Filename: services/build_service.py


import os

from flask import current_app
from base import db
from base.errors import ParamsError
from models.models import BuildLogModel, LOG_STATUS
from .project_service import Project
from .user_service import User
from .gitlab_service import GitLab
from . import handle_page, gen_version_num
from utils.time_utils import str2tsp, datetime_2_str_by_format, dt2ts
from utils import async_func




class Build():
    """
    制品
    """
    @classmethod
    def list_build(cls, keyword=None, user_id=None, type_id=None,
                   group_id=None, env=None, page_num=1, page_size=999,
                   project_id_list=[]):
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
        if project_id_list:
            project_params["id_list"] = project_id_list

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
        build_obj_list = build_obj_list.order_by(BuildLogModel.dt_created.desc()).all()

        build_dict_list = dict()
        need_user_id_list = list()
        for i in build_obj_list:
            if i.project_id in build_dict_list:
                continue

            build_dict = {
                "version_num": i.title,
                "creator": i.creator,
                "last_status": {
                    "code": i.status,
                    "value": dict(LOG_STATUS).get(i.status)
                },
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
                "name": "未知"
            }

        ret = {
            "data_list": project_list,
            "count": project_data["count"]
        }
        return ret

    @classmethod
    def query_build(cls, project_id):
        ret_data = cls.list_build(project_id_list=[project_id])
        if ret_data and ret_data["data_list"]:
            ret = ret_data["data_list"][0]
            return ret
        raise ParamsError("参数错误")


class BuildLog():
    """
    制品日志
    """
    @classmethod
    def list_build_log(cls, project_id, status_id=None, env=None,
                       page_num=1, page_size=999, type_id=None,
                       group_id=None, branch=None):
        log_obj_list = BuildLogModel.query.filter_by(project_id=project_id,
                                                     is_deleted=False).order_by(BuildLogModel.id.desc())
        if status_id:
            log_obj_list = log_obj_list.filter_by(status=status_id)
        if env:
            log_obj_list = log_obj_list.filter_by(env=env)
        if branch:
            log_obj_list = log_obj_list.filter_by(branch=branch)
        if group_id:
            log_obj_list = log_obj_list.filter_by(group_id=group_id)
        if type_id:
            log_obj_list = log_obj_list.filter_by(type_id=type_id)

        count = log_obj_list.count()
        log_obj_list = handle_page(log_obj_list, page_num, page_size)

        log_list = list()
        user_id_list = list()
        for i in log_obj_list:
            log_dict = i.to_dict()
            log_dict["version_num"] = log_dict["title"]
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
                    "name": "未知"
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
    def add_build_log(cls, project_id, branch, env, commit_id=None, user_id=0):
        project_dict = Project.query_project(project_id, False)
        try:
            job_type = project_dict["job"]["name"]
        except:
            raise ParamsError(f"{project_dict['name']}项目未设置编程语言")

        if not os.path.isfile(f"./base/pack_scripts/pack_{job_type.lower()}.sh"):
            raise ParamsError(f"项目的脚本配置错误.")

        source_project_id = project_dict["source_project_id"]
        if not commit_id:
            commit_id = GitLab.query_commit(source_project_id, branch)
            if commit_id:
                commit_id = commit_id["id"]
        else:
            # TODO 如果打包最小单元是commit则需要根据commit处理
            pass

        http_url = project_dict["http_url"]
        name = project_dict["name"]

        name = name.replace(" ", "_")
        log_count = BuildLogModel.query.filter_by(project_id=project_id,
                                                  branch=branch).count()
        tar_file_name = gen_version_num(name, log_count+1, env, branch)

        # 获取上次commit
        try:
            last_commit = BuildLogModel.query \
                .filter_by(project_id=project_id,
                           branch=branch) \
                .order_by(BuildLogModel.id.desc()).limit(1).commit_hash
        except Exception as e:
            last_commit = ""

        commit_text = ""
        new_commit_list = GitLab.list_commit(source_project_id, branch)
        for i in new_commit_list:
            if i.id == last_commit:
                break
            commit_text += f"{i.title}\n"

        build_log_dict = {
            "version_num": tar_file_name,
            "title": f"#{log_count+1} 【{branch}】{env}",
            "env": env,
            "project_id": project_id,
            "branch": branch,
            "commit_hash": commit_id,
            "status": 1, # TODO
            "creator": user_id,
            "build_type": 1,
            "type_id": project_dict["type_id"],
            "group_id": project_dict["group_id"],
            "commit_text": commit_text,
            "log_text": ">>: Ready for work.."
        }
        build_obj = BuildLogModel(**build_log_dict)
        db.session.add(build_obj)
        db.session.commit()

        repository_dir = current_app.config["REPOSITORY_DIR"]
        pro_dir = f"{repository_dir}/logs"
        if not os.path.exists(pro_dir):
            os.mkdir(pro_dir)

        log_file = f"{pro_dir}/{build_log_dict['version_num']}.log"
        with open(log_file, "w") as e:
            e.write(">>: Ready for work.. \n\n")

        build_id = build_obj.id
        try:
            params_d = {
                "build_log_id": build_id,
                "name": name,
                "tar_file_name": tar_file_name,
                "source_project_id": source_project_id,
                "branch": branch,
                "log_file": log_file,
                "job_type": job_type,
                "env": env
            }
            cls.async_clone_project(**params_d)
        except Exception as s:
            build_obj = BuildLogModel.query.get(build_id)
            build_obj.status = 3
            db.session.commit()
            with open(log_file, "a") as e:
                e.write(f">>: Build Error: {str(s)}\n")
            raise ParamsError(f"Build Err! Clone Err {str(s)}")

        return build_obj.id

    @classmethod
    @async_func
    def async_clone_project(cls, build_log_id, name, tar_file_name, source_project_id,
                            branch, log_file, job_type, env):
        try:
            from base import db
            from application import app
            with app.app_context():
                with open(log_file, "a") as e:
                    e.write(f">>: Query Build Info ..\n")
                build_obj = BuildLogModel.query.get(build_log_id)
                with open(log_file, "a") as e:
                    e.write(f">>: Clone Project Start..\n")
                with open(log_file, "a") as e:
                    tag, tar_file_dict = GitLab.clone_project(name, tar_file_name, source_project_id, branch, log_file, job_type, env)
                    if not tag:
                        build_obj.status = 3
                        e.write(tar_file_dict)
                        e.write(f">>: log file name is {log_file}\n\n")
                    else:
                        e.write(f">>: Clone Project End..\n")
                        e.write(f">>: Build Success! \n tar file name is {tar_file_name}\n\n")
                        e.write(f">>: log file name is {log_file}\n\n")
                        e.write(f"Success!!!\n")
                        build_obj.status = 2
                        build_obj.file_path = tar_file_dict["path"]

                with open(log_file, "r") as e:
                    build_obj.log_text = e.read()
                # query log
                db.session.commit()
        except Exception as s:
            build_obj = BuildLogModel.query.get(build_log_id)
            build_obj.status = 3
            db.session.commit()
            with open(log_file, "a") as e:
                e.write(f">>: Build Error: {str(s)}\n")
            raise ParamsError(f"Build Err! Clone Err {str(s)}")
        return

    @classmethod
    def query_log(cls, log_id):
        try:
            log_obj = BuildLogModel.query.get(log_id)
        except Exception as e:
            raise ParamsError(f"日志错误, {str(e)}")

        if log_obj.status in (2, 3):
            is_not_finished = 0
            log_text = log_obj.log_text
        else:
            is_not_finished = 1
            try:
                repository_dir = current_app.config["REPOSITORY_DIR"]
                log_file = f"{repository_dir}/logs/{log_obj.version_num}.log"
                with open(log_file) as e:
                    log_text = e.read()
            except Exception as e:
                raise ParamsError(f"log err {str(e)}")

        # down
        h = current_app.config["DOWNLOAD_HOST"]
        a = "/api/interface/v1/utils/download/"
        p = log_obj.file_path

        # user
        try:
            user_dict = User.query_user(log_obj.creator)
            user_name = user_dict["name"]
        except:
            user_name = "未知"

        status_dict = {
            "id": log_obj.status,
            "name": dict(LOG_STATUS).get(log_obj.status, "")
        }

        ret = log_obj.to_dict()
        ret["log_text"] = log_text
        ret["is_not_finished"] = is_not_finished
        ret["commit_list"] = ret["commit_text"].splitlines()
        ret["version_num"] = ret["title"]
        ret["operator_name"] = user_name
        ret["download_url"] = f"{h}{a}{p}"

        ret["duration"] = str2tsp(ret["dt_updated"]) - str2tsp(ret["dt_created"])
        ret["fetch_duration"] = ret["duration"]

        return ret
