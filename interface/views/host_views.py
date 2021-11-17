#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# Create: 2021-11-17 18:24:18
# Author: huihui - sunjiehuimail@foxmail.com
# Filename: interface/views/host_views.py


from api import Api

from services import calculate_page
from services.host_service import HostServer


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
        pass
