#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# Create: 2021-10-21 17:22:47
# Author: huihui - sunjiehuimail@foxmail.com
# Filename: services/project_service.py


from base import db
from base.errors import ParamsError
from models.models import ProjectModel, BuildScriptModel, SCRIPT_TYPE
from models.models import UserGroupModel
from . import handle_page
from utils.time_utils import datetime_2_str_by_format


class Project():
    """
    项目/仓库
    """
    @classmethod
    def add_project(cls, name, http_url, desc=None, ssh_url=None,
                    group_id=None, type_id=None, script=None,
                    script_type=None, archive_path=None, script_path=None,
                    source_project_id=None):
        """
        新增项目(正常不对外)
        """
        project_dict = {
            "name": name,
            "http_url": http_url,
        }

        if desc:
            project_dict["desc"] = desc
        if ssh_url:
            project_dict["ssh_url"] = ssh_url
        if group_id is not None:
            project_dict["group_id"] = group_id
        if type_id:
            project_dict["type_id"] = type_id
        if source_project_id:
            project_dict["source_project_id"] = source_project_id

        project = ProjectModel(**project_dict)

        db.session.add(project)

        if not script:
            db.session.commit()
        else:
            db.session.flush()

            try:
                for k, v in script.items():
                    tmp_dict = {
                        "env": k,
                        "project_id": project.id,
                        "execute_comm": v,
                        "script_type": script_type,
                        "script_path": script_path,
                        "archive_path": archive_path,
                    }
                    tmp = BuildScriptModel(**tmp_dict)
                    db.session.add(tmp)

                db.session.commit()
            except Exception as e:
                db.session.rollback()
                raise ParamsError(str(e))

        return

    @classmethod
    def list_project(cls, type_id=None, keyword=None, group_ids=None, user_ids=None,
                     id_list=None, need_git_info=True, page_num=1, page_size=999,
                     group_id=None, is_base=False):
        """
        项目列表
        """
        project_obj_list = ProjectModel.query.filter_by(is_deleted=False)
        if type_id:
            project_obj_list = project_obj_list.filter_by(type_id=type_id)
        if group_id:
            group_ids = str(group_id)
        if keyword:
            project_obj_list = project_obj_list.filter(ProjectModel.name.like(f"%{keyword}%"))
        if group_ids:
            project_obj_list = project_obj_list.filter(ProjectModel.group_id.in_(group_ids.split(",")))
        if id_list:
            project_obj_list = project_obj_list.filter(ProjectModel.id.in_(id_list))

        if user_ids is not None:
            u_tmp_obj_list = UserGroupModel.query.filter(UserGroupModel.user_id.in_(user_ids.split(",")))
            group_id_list = [i.group_id for i in u_tmp_obj_list]
            project_obj_list = project_obj_list.filter(ProjectModel.group_id.in_(group_id_list))

        count = project_obj_list.count()
        project_obj_list = handle_page(project_obj_list, page_num, page_size)

        project_list = list()
        source_project_id_list = list()
        for i in project_obj_list:
            source_project_id_list.append(i.source_project_id)
            project_list.append(i.to_dict())

        if is_base:
            need_git_info = False

        if project_list and need_git_info:
            # 由于同步项目写错地方了, 避免循环引用, 暂时内部引用
            from services.gitlab_service import GitLab

            """
            由于gitlab没有获取指定多个项目
            经测试, 获取10次get大概1-3秒, 获取1次所有(300个)项目大概5-7秒
            git_project_list = GitLab.list_project()
            print(">>: ", int(time.time()) - start_time)
            git_project_dict_list = dict()
            for i in git_project_list:
                if i.id not in source_project_id_list:
                    continue
                git_project_dict_list[i.id] = {
                    "last_activity_at": i.last_activity_at
                }

            """

            for i in project_list:
                if not i["source_project_id"]:
                    continue
                p = GitLab.get_project(i["source_project_id"])
                if p:
                    dt_last_submit = p.last_activity_at
                    dt_last_submit = dt_last_submit.split(".")[0].replace("T", " ")
                    i["dt_last_submit"] = dt_last_submit
        ret = {
            "data_list": project_list,
            "count": count
        }
        return ret

    @classmethod
    def query_project(cls, project_id, need_detail=True, is_local_project=True):
        if is_local_project:
            project_obj = ProjectModel.query.get(project_id)
        else:
            project_obj = ProjectModel.query.filter_by(source_project_id=project_id).one_or_none()

        if not project_obj or project_obj.is_deleted:
            raise ParamsError("Project Not Exist or Use Delete")

        project_dict = project_obj.to_dict()

        if not need_detail:
            return project_dict

        build_script_obj_list = BuildScriptModel.query \
            .filter_by(project_id=project_id,
                       is_deleted=False).all()
        if not build_script_obj_list:
            project_dict["script"] = dict()
            project_dict["script_type"] = dict()
            project_dict["archive_path"] = ""
        else:
            project_dict["script"] = dict()
            for i in build_script_obj_list:
                project_dict["script"][i.env] = i.execute_comm
                project_dict["script_type"] = {
                    "id": i.script_type,
                    "value": dict(SCRIPT_TYPE)[i.script_type]
                }
                project_dict["archive_path"] = i.archive_path

        return project_dict

    @classmethod
    def update_project(cls, id, name=None, http_url=None, desc=None,
                       ssh_url=None, group_id=None, type_id=None, script=None,
                       script_type=None, archive_path=None, script_path=None):
        """
        更新项目
        """
        project_obj = ProjectModel.query.get(id)

        if not project_obj:
            raise ParamsError("Update Err! Project Not Exist or Use Delete")

        if name:
            project_obj.name = name
        if http_url:
            project_obj.http_url = http_url
        if desc:
            project_obj.desc = desc
        if ssh_url:
            project_obj.ssh_url = ssh_url
        if group_id:
            project_obj.group_id = group_id
        if type_id:
            project_obj.type_id = type_id

        if script:
            try:
                for k, v in script.items():
                    script_obj = BuildScriptModel.query.filter_by(project_id=id,
                                                                  is_deleted=False,
                                                                  env=k).one_or_none()

                    if script_obj:
                        # 已存在的环境配置
                        script_obj.execute_comm = v
                        if script_type:
                            script_obj.script_type = script_type
                        if script_path:
                            script_obj.script_path = script_path
                        if archive_path:
                            script_obj.archive_path = archive_path
                    else:
                        # 不存在的环境配置
                        tmp_dict = {
                            "env": k,
                            "project_id": id,
                            "execute_comm": v,
                            "script_type": script_type,
                            "script_path": script_path,
                            "archive_path": archive_path,
                        }
                        tmp = BuildScriptModel(**tmp_dict)
                        db.session.add(tmp)
                    db.session.flush()
            except Exception as e:
                db.session.rollback()
                raise ParamsError(str(e))
        db.session.commit()

        return
