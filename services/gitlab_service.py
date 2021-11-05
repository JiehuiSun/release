#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# Create: 2021-10-27 15:35:27
# Author: huihui - sunjiehuimail@foxmail.com
# Filename: gitlab_service.py


import os
import gitlab
import shutil
from flask import current_app

from base.errors import InvalidArgsError
from services.project_service import Project




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

    @classmethod
    def sync_project(cls):
        """
        同步项目，如果开通其他来源的项目，需以source_id区分处理
        """
        projects = cls.list_project()

        project_dict_list = dict()
        for i in projects:
            project_dict = dict()
            project_dict["source_project_id"] = i.id
            project_dict["name"] = i.name
            project_dict["desc"] = i.description
            project_dict["http_url"] = i.http_url_to_repo
            project_dict["ssh_url"] = i.ssh_url_to_repo
            project_dict["group_id"] = 0
            project_dict_list[i.id] = project_dict

        project_data = Project.list_project()
        exist_project_id_list = list()
        for i in project_data["data_list"]:
            exist_project_id_list.append(i["source_project_id"])

        need_project_id_list = list(set(list(project_dict_list.keys())) - set(exist_project_id_list))
        for i in need_project_id_list:
            Project.add_project(**project_dict_list[i])

        return

    @classmethod
    def clone_project(cls, name, tar_file_name, project_id, branch="master"):
        """
        同步项目，如果开通其他来源的项目，需以source_id区分处理
        """
        repository_dir = current_app.config["REPOSITORY_DIR"]
        pro_dir = f"{repository_dir}/{name}"
        if not os.path.exists(pro_dir):
            os.mkdir(pro_dir)

        tmp_dir = f"{pro_dir}/{name}"
        if os.path.exists(tmp_dir):
            shutil.rmtree(tmp_dir)

        try:
            project = cls.gitlab().projects.get(project_id)
            tgz = project.repository_archive(branch)
        except Exception as e:
            # TODO 日志
            raise InvalidArgsError(f"Clone Err! {str(e)}")

        tar_file_path = f"{pro_dir}/{tar_file_name}.tar.gz"
        with open(tar_file_path, "wb") as t:
            t.write(tgz)

        if os.path.exists(tmp_dir):
            shutil.rmtree(tmp_dir)

        ret = {
            "file_name": tar_file_name,
            "path": tar_file_path.replace(f"{repository_dir}/", "")
        }
        return ret

    @classmethod
    def list_project(cls):
        """
        项目列表

        不支持多个id搜索, 只能后期加keyword
        """
        try:
            projects = cls.gitlab().projects.list(all=True)
        except Exception as e:
            raise InvalidArgsError(f"List Project Err! GitLab Config Err. {str(e)}")
        return projects

    @classmethod
    def get_project(cls, project_id):
        """
        获取项目
        """
        try:
            project = cls.gitlab().projects.get(project_id)
        except Exception as e:
            raise InvalidArgsError(f"Get Project Err! GitLab Config Err. {str(e)}")
        return project
