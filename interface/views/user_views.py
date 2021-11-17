#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# Create: 2021-10-09 19:21:21
# Author: huihui - sunjiehuimail@foxmail.com
# Filename: user_views.py


from api import Api

from services import calculate_page
from services.user_service import Group, User, Role, Job


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

        user_data = User.list_user(need_detail=True, **self.data)

        ret = {
            "data_list": user_data["data_list"],
            "count": user_data["count"],
            "page_num": self.data["page_num"],
            "page_size": self.data["page_size"],
            "page_count": calculate_page(user_data["count"])
        }

        return self.ret(data=ret)

    def put(self):
        self.params_dict = {
            "id": "required int",
            "role_id_list": "optional list",
            "group_id_list": "optional list",
            "job_id": "optional int",
            "desc": "optional str"
        }

        try:
            User.update_user(**self.data)
        except Exception as e:
            return self.ret(errcode=10000, errmsg=str(e))

        return self.ret()

    def get(self):
        try:
            user_dict = User.query_user(self.key)
        except Exception as e:
            return self.ret(errcode=10000, errmsg=str(e))

        return self.ret(data=user_dict)


class RoleView(Api):
    """
    角色
    """
    def list(self):
        self.params_dict = {
            "type_id": "optional str",
            "keyword": "optional str",
            "page_num": "optional str",
            "page_size": "optional str"
        }

        self.ver_params()

        self.handle_page_params()

        role_data = Role.list_role(**self.data)

        ret = {
            "data_list": role_data["data_list"],
            "count": role_data["count"],
            "page_num": self.data["page_num"],
            "page_size": self.data["page_size"],
            "page_count": calculate_page(role_data["count"])
        }

        return self.ret(data=ret)

    def get(self):
        role_dict = Role.query_role(self.key)

        return self.ret(data=role_dict)

    def post(self):
        self.params_dict = {
            "name": "required str",
            "type_id": "optional int",
            "menu_list": "required list",
            "comment": "optional str"
        }

        self.ver_params()

        try:
            Role.add_role(**self.data)
        except Exception as e:
            return self.ret(errcode=10000, errmsg=str(e))

        return self.ret()

    def put(self):
        self.params_dict = {
            "id": "required int",
            "name": "required str",
            "type_id": "optional int",
            "menu_list": "required list",
            "comment": "optional str"
        }

        self.ver_params()

        try:
            Role.update_role(**self.data)
        except Exception as e:
            return self.ret(errcode=10000, errmsg=str(e))

        return self.ret()

    def delete(self):
        self.params_dict = {
            "id": "required int"
        }

        self.ver_params()

        Role.del_role(**self.data)

        return self.ret()

class SelfInfoView(Api):
    def list(self):
        try:
            user_id = self.user_id
            user_dict = User.query_user(user_id)
        except Exception as e:
            return self.ret(errcode=10000, errmsg=str(e))

        return self.ret(data=user_dict)


class JobView(Api):
    def list(self):
        job_list = Job.list_job()

        ret = {
            "data_list": job_list
        }

        return self.ret(data=ret)
