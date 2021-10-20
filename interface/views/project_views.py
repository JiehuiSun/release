#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# Create: 2021-10-11 15:13:45
# Author: huihui - sunjiehuimail@foxmail.com
# Filename: project_views.py


from api import Api


class ProjectView(Api):
    """
    项目
    """
    def list(self):
        self.params_dict = {
            "type_id": "optional str",
            "group_id": "optional str",
        }

        self.ver_params()

        project_list = list()

        for i in range(2):
            project_dict = {
                "id": i + 1,
                "name": f"项目{i + 1}",
                "desc": f"项目{i + 1}的简介",
                "dt_last_submit": "2021-10-10 12:12:12",    # 实事获取
                # "dt_last_build": "2021-10-10 12:12:12",
            }
            project_list.append(project_dict)

        ret = {
            "data_list": project_list
        }

        return self.ret(data=ret)

    def get(self):
        self.params_dict = {
        }

        self.ver_params()

        project_dict = {
            "id": self.key,
            "name": "项目名name",
            "desc": "简介desc",
            "ssh_url": "ssl://asdfasdf.com/asdfasdf",
            "http_url": "http://asdfasdf.com/asdfasdf",
            "script": {
                "test": "big-text",
                "pro": "big-text"
            },
            "archive_path": "./hui/test",
            "script_type": {
                "id": 1,
                "value": "py"
            },
        }

        return self.ret(data=project_dict)
