#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# Create: 2021-10-27 15:35:27
# Author: huihui - sunjiehuimail@foxmail.com
# Filename: gitlab_service.py


import os
import gitlab
import tarfile
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

        branch_list = branch = project.branches.list(all=True)

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

        project_data = Project.list_project(is_base=True)
        exist_project_id_list = list()
        for i in project_data["data_list"]:
            exist_project_id_list.append(i["source_project_id"])

        need_project_id_list = list(set(list(project_dict_list.keys())) - set(exist_project_id_list))
        for i in need_project_id_list:
            Project.add_project(**project_dict_list[i])

        return

    @classmethod
    def clone_project(cls, name, tar_file_name, project_id, branch="master", log_file=None, job_type=None, env="dev"):
        """
        同步项目，如果开通其他来源的项目，需以source_id区分处理
        直接打好包
        """
        if not log_file:
            log_file = f"./{tar_file_name}.log"
        with open(log_file, "a") as e:
            e.write("Handle dir \n")
        repository_dir = current_app.config["REPOSITORY_DIR"]
        pro_dir = f"{repository_dir}/{name}"
        if not os.path.exists(pro_dir):
            os.mkdir(pro_dir)

        # TODO
        tmp_dir = f"{pro_dir}/{name}"
        # if os.path.exists(tmp_dir):
            # shutil.rmtree(tmp_dir)

        with open(log_file, "a") as e:
            e.write("git pull project..\n")

        try:
            # 区分是否需要不构建
            project_dict = Project.query_project(project_id,
                                                 is_local_project=False)
            if project_dict.get("is_build"):
                t_name = f"pack_{job_type.lower()}"
            else:
                t_name = f"pack_python" # 不用构建的
            base_file = f"./base/pack_scripts/{t_name}.sh"
            if not os.path.isfile(base_file):
                return False, "没有打包脚本\n"
            base_file = os.path.abspath(base_file)

            # 获取自定义脚本
            custom_comm_dict = project_dict["script"]
            if custom_comm_dict.get(env):
                custom_comm = custom_comm_dict[env]
            else:
                custom_comm = ""

            pack_func = getattr(cls, t_name)
            if not pack_func:
                return False, "项目语言脚本配置异常, 请检查项目及脚本配置以及打包入口\n"

            # commit v2
            tag, tgz = pack_func(project_id, branch, base_file, pro_dir, log_file, env, commit=None, custom_comm=custom_comm)
            # project = cls.gitlab().projects.get(project_id)
            # tgz = project.repository_archive(branch)
            if not tag:
                with open(log_file, "a") as e:
                    e.write(tgz)
                return False, "Build Err!\n"
        except Exception as s:
            # TODO 日志
            with open(log_file, "a") as e:
                e.write(">>: Error: pull project error..\n\n")
            return False, f"Clone Err! {str(s)}\n"

        with open(log_file, "a") as e:
            e.write("generate 'tar.gz' file..\n")
        # if job_type.lower() in ("web", "java"):
        if tgz:
            tar_file_path = f"{pro_dir}/{tar_file_name}.tar.gz"
            with tarfile.open(tar_file_path, "w:gz") as tar:
                tar.add(tgz, arcname=os.path.basename(tar_file_name))
        else:
            tar_file_path = ">> 该项目是无需打包的服务"
        # else:
        # with open(tar_file_path, "wb") as t:
            # t.write(tgz)

        with open(log_file, "a") as e:
            e.write(f"tar file ok. {tar_file_path}\n")
        # if os.path.exists(tmp_dir):
            # shutil.rmtree(tmp_dir)

        ret = {
            "file_name": tar_file_name,
            "path": tar_file_path.replace(f"{repository_dir}/", "")
        }
        return True, ret

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

    @classmethod
    def list_commit(cls, project_id, branch):
        """
        根据项目跟分支获取分支的commit最新列表
        """
        project = cls.get_project(project_id)
        commits = project.commits.list(ref_name=branch, page=0, per_page=20)

        return commits

    @classmethod
    def query_commit(cls, project_id, branch):
        """
        根据项目跟分支获取最新的commit信息
        """
        project = cls.get_project(project_id)
        branch = project.branches.get(branch)
        return branch.commit

    @classmethod
    def pack_python(cls, project_id, branch, base_file, pro_dir, log_file, env, commit=None, custom_comm=""):
        git_cmd = current_app.config["GIT_ABS_CMD"]
        project = cls.gitlab().projects.get(project_id)
        p_local_path = f"{pro_dir}/{project.name}"
        if not os.path.exists(p_local_path):
            project_url = project.ssh_url_to_repo.replace("op-gitlab.mumway.com", "gitlab.xiavan.cloud")
            clone_cmd = f"{git_cmd} clone {project_url} {p_local_path}"
            if os.system(f"{clone_cmd} >> {log_file}"):
                return False, "打包异常, 项目克隆失败\n"

        if os.system(f"cd {p_local_path} >> {log_file} 2>&1 && {git_cmd} checkout .&&{git_cmd} pull &&{git_cmd} checkout {branch} >> {log_file} 2>&1 && {git_cmd} pull origin {branch} >> {log_file} 2>&1"):
            return False, "打包异常, Git错误或脚本执行错误\n"

        return True, p_local_path

    @classmethod
    def pack_java(cls, project_id, branch, base_file, pro_dir, log_file, env, commit=None, custom_comm=""):
        git_cmd = current_app.config["GIT_ABS_CMD"]
        project = cls.gitlab().projects.get(project_id)
        p_local_path = f"{pro_dir}/{project.name}".replace(" ", "_")
        if not os.path.exists(p_local_path):
            project_url = project.ssh_url_to_repo.replace("op-gitlab.mumway.com", "gitlab.xiavan.cloud")
            clone_cmd = f"{git_cmd} clone {project_url} {p_local_path}"
            if os.system(f"{clone_cmd} >> {log_file}"):
                return False, "打包异常, 项目克隆失败\n"

        if not os.path.exists(f"{p_local_path}/ops_dev_path"):
            os.system(f"mkdir {p_local_path}/ops_dev_path")
        if os.system(f"cd {p_local_path} >> {log_file} 2>&1 &&{git_cmd} checkout .&&{git_cmd} pull && {git_cmd} checkout {branch} >> {log_file} 2>&1 && {git_cmd} pull origin {branch} >> {log_file} 2>&1 &&/bin/bash {base_file} {env} >> {log_file} 2>&1"):
            return False, "打包异常, Git错误或脚本执行错误\n"
        ret_dir = f"{p_local_path}/ops_dev_path"

        return True, ret_dir

    @classmethod
    def pack_php(cls, project_id, branch, base_file, pro_dir, log_file, env, commit=None, custom_comm=""):
        git_cmd = current_app.config["GIT_ABS_CMD"]
        project = cls.gitlab().projects.get(project_id)
        p_local_path = f"{pro_dir}/{project.name}"
        if not os.path.exists(p_local_path):
            project_url = project.ssh_url_to_repo.replace("op-gitlab.mumway.com", "gitlab.xiavan.cloud")
            clone_cmd = f"{git_cmd} clone {project_url} {p_local_path}"
            if os.system(f"{clone_cmd} >> {log_file}"):
                return False, "打包异常, 项目克隆失败\n"

        if os.system(f"cd {p_local_path} >> {log_file} 2>&1 &&{git_cmd} checkout .&&{git_cmd} pull && {git_cmd} checkout {branch} >> {log_file} 2>&1 && {git_cmd} pull origin {branch} >> {log_file} 2>&1"):
            return False, "打包异常, Git错误或脚本执行错误\n"

        return True, p_local_path

    @classmethod
    def pack_go(cls, project_id, branch, base_file, pro_dir, log_file, env, commit=None, custom_comm=""):
        return True, True

    @classmethod
    def pack_web(cls, project_id, branch, base_file, pro_dir, log_file, env, commit=None, custom_comm=""):
        """
        TODO 默认配置使用bash, 项目配置使用text的shell, 后期做兼容.
        """
        git_cmd = current_app.config["GIT_ABS_CMD"]
        project = cls.gitlab().projects.get(project_id)
        p_local_path = f"{pro_dir}/{project.name.strip()}"
        if not os.path.exists(p_local_path):
            project_url = project.ssh_url_to_repo.replace("op-gitlab.mumway.com", "gitlab.xiavan.cloud")
            clone_cmd = f"{git_cmd} clone {project_url} {p_local_path}"
            if os.system(f"{clone_cmd} >> {log_file}"):
                return False, "打包异常, 项目克隆失败\n"

        a = os.system(f"cd {p_local_path} >> {log_file} 2>&1 &&{git_cmd} checkout .&&{git_cmd} pull &&{git_cmd} checkout {branch} >> {log_file} 2>&1 && {git_cmd} pull origin {branch} >> {log_file} 2>&1")
        if a:
            return False, f"打包异常, Git错误或仓库错乱, 错误代码{a}\n"
        if not custom_comm:
            a = os.system(f"cd {p_local_path} && /bin/bash {base_file} {env} >> {log_file} 2>&1")
            if a:
                return False, f"打包异常, 默认脚本执行错误, 错误代码{a}\n"
        else:
            c = [f"cd {p_local_path}"]
            for i in custom_comm.splitlines():
                if i.strip():
                    c.append(i.strip())
            cc = f">> {log_file} 2>&1 &&".join(c)
            cc += f">> {log_file} 2>&1"
            a = os.system(cc)
            if a:
                return False, f"打包异常, 自定义脚本执行错误, 错误代码{a}\n"

        ret_dir = f"{p_local_path}/dist"
        if not os.path.exists(ret_dir):
            ret_dir = f"{p_local_path}/dist_tmp"
            if not os.path.exists(ret_dir):
                os.system(f"mkdir {ret_dir}")
            os.system(f"rm -Rvf {ret_dir}/*")
            os.system(f"cp -R `find {p_local_path} -type d -path {p_local_path}/node_modules -prune -o -print | sed 1d ` {ret_dir}")

        return True, ret_dir

    @classmethod
    def pack_miniapp(cls, project_id, branch, base_file, pro_dir, log_file, env, commit=None, custom_comm=""):
        git_cmd = current_app.config["GIT_ABS_CMD"]
        project = cls.gitlab().projects.get(project_id)
        p_local_path = f"{pro_dir}/{project.name.strip()}"
        if not os.path.exists(p_local_path):
            project_url = project.ssh_url_to_repo.replace("op-gitlab.mumway.com", "gitlab.xiavan.cloud")
            clone_cmd = f"{git_cmd} clone {project_url} {p_local_path}"
            if os.system(f"{clone_cmd} >> {log_file}"):
                return False, "打包异常, 项目克隆失败\n"

        a = os.system(f"cd {p_local_path} >> {log_file} 2>&1 &&{git_cmd} checkout .&&{git_cmd} pull &&{git_cmd} checkout {branch} >> {log_file} 2>&1 && {git_cmd} pull origin {branch} >> {log_file} 2>&1")
        if a:
            return False, f"打包异常, Git错误或仓库错乱, 错误代码{a}\n"
        if not custom_comm:
            a = os.system(f"cd {p_local_path} && /bin/bash {base_file} {env} >> {log_file} 2>&1")
            if a:
                return False, f"打包异常, 默认脚本执行错误, 错误代码{a}\n"
        else:
            c = [f"cd {p_local_path}"]
            for i in custom_comm.splitlines():
                if i.strip():
                    c.append(i.strip())
            cc = f">> {log_file} 2>&1 &&".join(c)
            cc += f">> {log_file} 2>&1"
            a = os.system(cc)
            if a:
                return False, f"打包异常, 自定义脚本执行错误, 错误代码{a}\n"

        ret_dir = f"{p_local_path}/dist"
        return True, ret_dir
