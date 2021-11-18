#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# Create: 2021-10-18 17:40:40
# Author: huihui - sunjiehuimail@foxmail.com
# Filename: submit_views.py


import os
from api import Api
from flask import current_app

from services import calculate_page
from services.submit_service import Submit


class SubmitProjectView(Api):
    """
    制品项目(也是拿项目)
    """
    def list(self):
        self.params_dict = {
            "type_id": "optional str",
            "group_id": "optional str",
            "env": "optional str",
            "page_num": "optional str",
            "page_size": "optional str",
            "project_id": "optional str",
            "branch": "optional str",
        }

        self.ver_params()

        self.handle_page_params()

        submit_data = Submit.list_submit(**self.data)
        submit_list = submit_data["data_list"]

        ret = {
            "data_list": submit_list,
            "count": submit_data["count"],
            "page_num": self.data["page_num"],
            "page_size": self.data["page_size"],
            "page_count": calculate_page(submit_data["count"])
        }

        return self.ret(data=ret)

    def post(self):
        self.params_dict = {
            "log_id": "required int",
        }

        self.ver_params()

        # 记录
        self.data["user_id"] = self.user_id
        submit_dict = Submit.add_submit(**self.data)

        #  交付(可做异步)
        repository_dir = current_app.config["REPOSITORY_DIR"]
        file_path = os.path.join(repository_dir, submit_dict["file_path"])
        Submit.async_add_deploy(submit_dict["id"],
                                submit_dict["project_id"],
                                file_path,
                                submit_dict["env"])

        return self.ret()
