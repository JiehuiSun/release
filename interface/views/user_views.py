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
