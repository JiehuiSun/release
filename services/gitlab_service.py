#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# Create: 2021-10-27 15:35:27
# Author: huihui - sunjiehuimail@foxmail.com
# Filename: gitlab_service.py


import gitlab
from flask import current_app

from base.errors import InvalidArgsError




class GitLab():
    @classmethod
    def gitlab(cls):
        try:
            gl = gitlab.Gitlab(current_app.config["GITLAB_HOST"],
                               private_token=current_app.config["GITLAB_TOKEN"])
            gl.auth()
            return gl
        except Exception as e:
            current_app.logger.error(">> GitLab Err")
            raise InvalidArgsError(f"GitLab Server Err {str(e)}")

    @classmethod
    def list_branch(cls, project_id):
        """
        params: project_id gitlab的项目ID
        """
        try:
            project = cls.gitlab().projects.get(project_id)
        except Exception as e:
            raise InvalidArgsError(f"List Branch Err! Project Not Exist or GitLab Config Err. {str(e)}")

        branch_list = branch = project.branches.list()

        ret_list = list()
        for i in branch_list:
            branch_dict = dict()
            branch_dict["name"] = i.name
            branch_dict["commit"] = i.commit["title"]
            branch_dict["dt_last"] = i.commit["committed_date"]

            ret_list.append(branch_dict)

        ret_list = sorted(ret_list, key=lambda x: (x["dt_last"]), reverse=True)

        return ret_list
