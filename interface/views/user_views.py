#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# Create: 2021-10-09 19:21:21
# Author: huihui - sunjiehuimail@foxmail.com
# Filename: user_views.py


from api import Api

from services import calculate_page
from services.user_service import Group, User


class GroupView(Api):
    """
    组
    """
    def post(self):
        self.params_dict = {
            "name": "required str",
            "desc": "optional str",
            "parent_id": "optional int",
            "email": "optional str",
        }

        self.ver_params()

        try:
            Group.add_group(**self.data)
        except Exception as e:
            return self.ret(errcode=10000, errmsg=str(e))

        return self.ret()

    def list(self):
        self.params_dict = {
            "type_id": "optional str",
            "keyword": "optional str",
            "parent_id": "optional str",
            "page_num": "optional str",
            "page_size": "optional str"
        }

        self.ver_params()

        self.handle_page_params()

        group_data = Group.list_group(**self.data)

        ret = {
            "data_list": group_data["data_list"],
            "count": group_data["count"],
            "page_num": self.data["page_num"],
            "page_size": self.data["page_size"],
            "page_count": calculate_page(group_data["count"])
        }

        return self.ret(data=ret)


class UserView(Api):
    """
    用户
    """
    def list(self):
        self.params_dict = {
            "type_id": "optional str",
            "keyword": "optional str",
            "group_id": "optional str",
            "page_num": "optional str",
            "page_size": "optional str"
        }

        self.ver_params()

        self.handle_page_params()

        user_data = User.list_user(**self.data)

        ret = {
            "data_list": user_data["data_list"],
            "count": user_data["count"],
            "page_num": self.data["page_num"],
            "page_size": self.data["page_size"],
            "page_count": calculate_page(user_data["count"])
        }

        return self.ret(data=ret)
