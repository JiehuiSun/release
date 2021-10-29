#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# Create: 2021-10-18 17:40:40
# Author: huihui - sunjiehuimail@foxmail.com
# Filename: submit_views.py


from api import Api

from services.submit_service import Submit, SubmitLog


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

        submit_data = Submit.list_submit(**self.data)
        submit_list = submit_data["data_list"]

        ret = {
            "data_list": submit_list,
            "count": submit_data["count"]
        }

        return self.ret(data=ret)


class SubmitLogView(Api):
    """
    发布记录
    """
    def list(self):
        self.params_dict = {
            "project_id": "required str",
            "status_id": "optional str",
            "env": "optional str",
        }

        self.ver_params()

        submit_data = SubmitLog.list_submit_log(**self.data)

        ret = {
            "data_list": submit_data["data_list"],
            "count": submit_data["count"]
        }

        return self.ret(data=ret)

    def post(self):
        self.params_dict = {
            "project_id": "required int",
            "branch": "required str",
            "env": "required str",
            "commit_id": "optional str"
        }

        self.ver_params()

        """
        利用官网提供方法克隆项目(完整项目可能会慢)
        import subprocess
        subprocess.call(['git', 'clone', git_url])

        克隆需要利用缓存记录过程,
        在克隆前判断是否在克隆,
        并执行一次删除本地目录操作,
        防止克隆失败一次导致的错误
        """

        try:
            SubmitLog.add_submit_log(**self.data)
        except Exception as e:
            return self.ret(errcode=100000, errmsg=str(e))

        return self.ret()
