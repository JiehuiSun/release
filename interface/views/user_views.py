#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# Create: 2021-10-09 19:21:21
# Author: huihui - sunjiehuimail@foxmail.com
# Filename: user_views.py


from api import Api


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

        return self.ret()

    def list(self):
        self.params_dict = {
            "type_id": "optional str",
            "keyword": "optional str",
        }

        self.ver_params()

        group_list = list()

        for i in range(2):
            group_dict = {
                "id": i + 1,
                "name": f"组{i + 1}",
                "type": {
                    "id": 10,
                    "name": "后端组"
                }
            }
            group_list.append(group_dict)

        ret = {
            "data_list": group_list
        }

        return self.ret(data=ret)
