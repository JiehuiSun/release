#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# Create: 2021-10-27 15:34:54
# Author: huihui - sunjiehuimail@foxmail.com
# Filename: gitlab_views.py


from api import Api

from services.project_service import Project
from services.gitlab_service import GitLab
from services.requirement_service import Requirement


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
    NEED_LOGIN = False
    def post(self):
        if not self.data or self.data.get("object_kind") != "push":
            return self.ret(errcode=100000, errmsg="非法请求")

        source_project_id = self.data.get("project_id")
        branch = self.data.get("ref")
        if not source_project_id or not branch:
            return self.ret(errcode=100000, errmsg="非法请求")

        project_obj = Project.query_project(source_project_id,
                                            need_detail=False,
                                            is_local_project=False)
        branch = branch.split("/")[-1]

        if not project_obj:
            return self.ret(errcode=100000, errmsg="项目未同步")

        # TODO 获取现有需求, 判断是否自动构建
        params_ab = {
            "project_id": project_obj["id"],
            "status_id_ge": 604,
            "status_id_le": 601,
            "branch": branch
        }
        need_auto_build_list = Requirement.list_auto_build_requirement(**params_ab)
        if not need_auto_build_list:
            print(f"{project_obj['name']}-{branch}没有需要自动构建的需求")
            return self.ret()

        from services.build_service import BuildLog
        need_list = dict()
        for i in need_auto_build_list:
            params_a = {
                "project_id": i["project_id"],
                "env": i["env"],
                "branch": branch
            }
            p_b_e = f"{params_a['project_id']}|{params_a['env']}|{params_a['branch']}"
            if p_b_e not in need_list:
                need_list[p_b_e] = params_a
        for i in need_list.values():
            # 构建
            BuildLog.add_build_log(user_id=9999, **i)

        return self.ret()
