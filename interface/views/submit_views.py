#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# Create: 2021-10-18 17:40:40
# Author: huihui - sunjiehuimail@foxmail.com
# Filename: submit_views.py


from api import Api

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
            "log_id": "required str",
        }

        self.ver_params()

        return self.ret()
