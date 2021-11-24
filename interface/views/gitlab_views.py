#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# Create: 2021-10-27 15:34:54
# Author: huihui - sunjiehuimail@foxmail.com
# Filename: gitlab_views.py


from api import Api

from services.project_service import Project
from services.gitlab_service import GitLab


class BranchView(Api):
    """
    分支
    """
    def list(self):
        self.params_dict = {
            "project_id": "required str",
        }

        self.ver_params()

        project_dict = Project.query_project(self.data["project_id"],
                                            need_detail=False)

        source_project_id = project_dict["source_project_id"]

        branch_list = GitLab.list_branch(source_project_id)

        ret = {
            "data_list": branch_list
        }

        return self.ret(data=ret)


class SyncProjectView(Api):
    """
    同步项目
    """
    def list(self):

        try:
            GitLab.sync_project()
        except Exception as e:
            return self.ret(errcode=100000, errmsg=f"{str(e)}")
        return self.ret()


class GitlabActionView(Api):
    """
    git动作webhook
    """
    def post(self):
        return self.ret()
