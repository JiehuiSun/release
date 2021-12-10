#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# Create: 2021-10-11 15:13:45
# Author: huihui - sunjiehuimail@foxmail.com
# Filename: project_views.py


from api import Api

from services import calculate_page
from services.project_service import Project


class ProjectView(Api):
    """
    项目
    """
    def list(self):
        self.params_dict = {
            "type_id": "optional str",
            "group_ids": "optional str",
            "user_ids": "optional str",
            "is_base": "optional str",
            "page_num": "optional str",
            "page_size": "optional str"
        }

        self.ver_params()

        self.handle_page_params()

        project_data = Project.list_project(**self.data)

        ret = {
            "data_list": project_data["data_list"],
            "count": project_data["count"],
            "page_num": self.data["page_num"],
            "page_size": self.data["page_size"],
            "page_count": calculate_page(project_data["count"])
        }

        return self.ret(data=ret)

    def get(self):
        self.params_dict = {
        }

        self.ver_params()

        project_dict = Project.query_project(self.key)

        return self.ret(data=project_dict)

    def post(self):
        self.params_dict = {
            "name": "required str",
            "desc": "optional str",
            "ssh_url": "optional str",
            "http_url": "required str",
            "group_id": "optional int",
            "type_id": "optional int",
            "script": "optional pass",
            "script_type": "optional int",
            "archive_path": "optional str",
            "script_path": "optional str",
            "source_project_id": "optional pass",
            "is_build": "optional pass",
        }

        self.ver_params()

        try:
            Project.add_project(**self.data)
        except Exception as e:
            return self.ret(errcode=100000, errmsg=str(e))

        return self.ret()

    def put(self):
        self.params_dict = {
            "id": "required int",
            "name": "optional str",
            "desc": "optional str",
            "ssh_url": "optional str",
            "http_url": "optional str",
            "group_id": "optional int",
            "type_id": "optional int",
            "script": "optional pass",
            "script_type": "optional int",
            "archive_path": "optional str",
            "script_path": "optional str",
            "source_project_id": "optional pass",
            "is_build": "optional pass",
        }

        self.ver_params()

        try:
            Project.update_project(**self.data)
        except Exception as e:
            return self.ret(errcode=100000, errmsg=str(e))

        return self.ret()
