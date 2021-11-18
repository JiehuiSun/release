#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# Create: 2021-11-17 18:24:18
# Author: huihui - sunjiehuimail@foxmail.com
# Filename: interface/views/host_views.py


from api import Api

from services import calculate_page
from services.host_service import HostServer, ProjectHost


class HostView(Api):
    """
    主机信息
    """
    def list(self):
        self.params_dict = {
            "keyword": "optional str",
            "page_num": "optional str",
            "page_size": "optional str",
        }

        self.ver_params()

        self.handle_page_params()

        host_data = HostServer.list_host(**self.data)

        ret = {
            "data_list": host_data["data_list"],
            "count": host_data["count"],
            "page_num": self.data["page_num"],
            "page_size": self.data["page_size"],
            "page_count": calculate_page(host_data["count"])
        }

        return self.ret(data=ret)

    def post(self):
        self.params_dict = {
            "name": "required str",
            "hostname": "required str",
            "port": "optional int",
            "username": "required str",
            "pkey": "required str",
            "desc": "optional str",
        }

        self.ver_params()

        self.data["user_id"] = self.user_id

        HostServer.add_host(**self.data)

        return self.ret()

    def put(self):
        self.params_dict = {
            "id": "required int",
            "name": "optional str",
            "hostname": "optional str",
            "port": "optional int",
            "username": "optional str",
            "pkey": "optional str",
            "desc": "optional str",
        }

        self.ver_params()

        self.data["user_id"] = self.user_id
        HostServer.update_host(**self.data)

        return self.ret()

    def delete(self):
        self.params_dict = {
            "id": "required int",
        }

        self.ver_params()

        HostServer.del_host(**self.data)

        return self.ret()

    def get(self):
        self.params_dict = {
        }

        self.ver_params()

        self.handle_page_params()

        host_dict = HostServer.query_host(self.key)

        return self.ret(data=host_dict)


class HostProjectView(Api):
    """
    主机信息
    """
    def list(self):
        self.params_dict = {
            "keyword": "optional str",
            "page_num": "optional str",
            "page_size": "optional str",
        }

        self.ver_params()

        self.handle_page_params()

        host_data = ProjectHost.list_host(**self.data)

        ret = {
            "data_list": host_data["data_list"],
            "count": host_data["count"],
            "page_num": self.data["page_num"],
            "page_size": self.data["page_size"],
            "page_count": calculate_page(host_data["count"])
        }

        return self.ret(data=ret)

    def post(self):
        self.params_dict = {
            "name": "required str",
            "host_id_list": "required list",
            "project_id": "required int",
            "path": "required str",
            "env": "required str",
            "service_path": "optional str",
            "ignore_text": "optional str",
            "script_text": "optional str",
        }

        self.ver_params()

        self.data["user_id"] = self.user_id

        ProjectHost.add_host(**self.data)

        return self.ret()

    def put(self):
        self.params_dict = {
            # "id": "required int",
            "name": "required str",
            "host_id_list": "required list",
            "project_id": "required int",
            "path": "required str",
            "env": "required str",
            "service_path": "optional str",
            "ignore_text": "optional str",
            "script_text": "optional str",
        }

        self.ver_params()

        self.data["user_id"] = self.user_id
        ProjectHost.update_host(**self.data)

        return self.ret()

    def delete(self):
        self.params_dict = {
            "project_id": "required int",
        }

        self.ver_params()

        ProjectHost.del_host(**self.data)

        return self.ret()

    def get(self):
        self.params_dict = {
        }

        self.ver_params()

        self.handle_page_params()

        host_dict = ProjectHost.query_host(self.key)

        return self.ret(data=host_dict)
