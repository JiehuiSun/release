#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# Create: 2021-10-19 14:22:21
# Author: huihui - sunjiehuimail@foxmail.com
# Filename: build_views.py


from api import Api

from services import calculate_page
from services.build_service import Build, BuildLog


class BuildProjectView(Api):
    """
    制品项目(也是拿项目)
    """
    def list(self):
        self.params_dict = {
            "type_id": "optional str",
            "group_id": "optional str",
            "env": "optional str",
            "page_num": "optional str",
            "page_size": "optional str"
        }

        self.ver_params()

        self.handle_page_params()

        build_data = Build.list_build(**self.data)
        build_list = build_data["data_list"]

        ret = {
            "data_list": build_list,
            "count": build_data["count"],
            "page_num": self.data["page_num"],
            "page_size": self.data["page_size"],
            "page_count": calculate_page(build_data["count"])
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
            "env": "optional str",
            "type_id": "optional str",
            "group_id": "optional str",
            "page_num": "optional str",
            "page_size": "optional str",
            "branch": "optional str",
        }

        self.ver_params()

        self.handle_page_params()

        build_data = BuildLog.list_build_log(**self.data)

        ret = {
            "data_list": build_data["data_list"],
            "count": build_data["count"],
            "page_num": self.data["page_num"],
            "page_size": self.data["page_size"],
            "page_count": calculate_page(build_data["count"])
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
            build_log_id = BuildLog.add_build_log(**self.data)
        except Exception as e:
            return self.ret(errcode=100000, errmsg=str(e))

        return self.ret(data={"id": build_log_id})


class BuildConsoleLogView(Api):
    """
    制品日志
    """
    def get(self):
        log_text = """
            aaa
            bbb
            ccc
            ddd
            eee
            """
        commit_list = [
            "feat(aaa): Commit Info111",
            "feat(bbb): Commit Info222",
        ]
        ret = {
            "log_text": log_text,
            "is_not_finished": 0,
            "commit_list": commit_list,
            "version_num": "111-2124142124",
            "dt_created": "2021-10-10 02:02:01",
            "duration": 66,
            "operator_name": "操作人1",
            "download_url": "/api/interface/v1/utils/download/?file=RedBull/26-pro-2021110506822(RedBull-master).tar.gz"
        }

        return self.ret(data=ret)
