#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# Create: 2021-10-19 14:22:21
# Author: huihui - sunjiehuimail@foxmail.com
# Filename: build_views.py


from api import Api


class BuildProjectView(Api):
    """
    制品项目(也是拿项目)
    """
    def list(self):
        self.params_dict = {
            "type_id": "optional str",
            "group_id": "optional str",
            "env_id": "optional str",
        }

        self.ver_params()

        build_list = list()

        for i in range(2):
            build_dict = {
                "id": i + 1,
                "name": f"项目{i + 1}",
                "desc": f"项目{i + 1}的简介",
                "dt_last_build": "2021-10-10 12:12:12",    # 实事获取
                "last_duration": 60,    # 上一次耗时(s)
                "last_status": {
                    "code": 1,
                    "value": "成功"
                },
                "operator": {
                    "id": 1,
                    "name": "狗子"
                }
            }
            build_list.append(build_dict)

        ret = {
            "data_list": build_list
        }

        return self.ret(data=ret)


class BuildLogView(Api):
    """
    发布记录
    """
    def list(self):
        self.params_dict = {
            "project_id": "required str",
            "status_id": "optional str",
            "env_id": "optional str",
        }

        self.ver_params()

        build_list = list()

        for i in range(2):
            build_dict = {
                "id": i + 1,
                "title": f"日志标题{i + 1}",
                "desc": f"日志{i + 1}的简介",
                "env": "test",
                "version_num": "版本号",
                "duration": 60,    # 上一次耗时(s)
                "commit": "commit信息",
                "status": {
                    "code": 1,
                    "value": "成功"
                },
                "operator": {
                    "id": 1,
                    "name": "狗子"
                }
            }
            build_list.append(build_dict)

        ret = {
            "data_list": build_list
        }

        return self.ret(data=ret)
