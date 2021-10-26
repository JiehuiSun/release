#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# Create: 2021-10-21 17:22:47
# Author: huihui - sunjiehuimail@foxmail.com
# Filename: services/project_service.py


from base import db
from base.errors import ParamsError
from models.models import ProjectModel, BuildScriptModel, SCRIPT_TYPE


class Project():
    """
    项目/仓库
    """
    @classmethod
    def add_project(cls, name, http_url, desc=None, ssh_url=None,
                    group_id=None, type_id=None, script=None,
                    script_type=None, archive_path=None, script_path=None):
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
        if group_id:
            project_dict["group_id"] = group_id
        if type_id:
            project_dict["type_id"] = type_id

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
                raise str(e)

        return

    @classmethod
    def list_project(cls, type_id=None, keyword=None, group_id=None, user_id=None):
        """
        项目列表
        """
        project_obj_list = ProjectModel.query.filter_by(is_deleted=False)
        if type_id:
            project_obj_list = project_obj_list.filter_by(type_id=type_id)
        if keyword:
            project_obj_list = project_obj_list.filter(ProjectModel.name.like(f"%{keyword}%"))
        if group_id:
            project_obj_list = project_obj_list.filter_by(group_id=group_id)

        count = project_obj_list.count()
        project_obj_list = project_obj_list.all()

        project_list = list()
        for i in project_obj_list:
            project_list.append(i.to_dict())

        ret = {
            "data_list": project_list,
            "count": count
        }
        return ret

    @classmethod
    def query_project(cls, project_id):
        project_obj = ProjectModel.query.get(project_id)

        if not project_obj or project_obj.is_deleted:
            raise ParamsError("Project Not Exist or Use Delete")

        project_dict = project_obj.to_dict()

        build_script_obj_list = BuildScriptModel.query \
            .filter_by(project_id=project_id,
                       is_deleted=False).all()
        if not build_script_obj_list:
            project_dict["script"] = dict()
            project_dict["script_type"] = dict()
            project_dict["archive_path"] = ""
        else:
            for i in build_script_obj_list:
                project_dict["script"][i.env] = i.execute_comm
                project_dict["script_type"] = {
                    "id": i.script_type,
                    "value": dict(SCRIPT_TYPE)[i.script_type]
                }
                project_dict["archive_path"] = i.archive_path

        return project_dict
