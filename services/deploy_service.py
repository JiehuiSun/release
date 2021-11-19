#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# Create: 2021-11-13 19:35:07
# Author: huihui - sunjiehuimail@foxmail.com
# Filename: deploy_service.py


from models.models import Hosts, HostProject
from models.models import SubmitLogModel
from services.ssh_service import SSH


class Deploy():
    """
    部署
    """
    @classmethod
    def add_deploy(cls, project_id, tarfile_path, env):
        host_project_obj_list = HostProject.query.filter_by(project_id=project_id,
                                                            is_deleted=False,
                                                            env=env).all()

        if not host_project_obj_list:
            raise "该仓库为配置主机或环境, 联系运维"

        host_dict_list = dict()
        for i in host_project_obj_list:
            host_dict_list[i.host_id] = {
                "path": i.path,
                "ignore_text": i.ignore_text,
                "script_text": i.script_text,
            }

        host_obj_list = Hosts.query.filter(Hosts.id.in_(list(host_dict_list.keys()))).all()
        if not host_obj_list:
            # 未配置主机信息
            raise "未配置主机信息, 联系运维"

        for i in host_obj_list:
            ssh = SSH(i.hostname, i.port, i.username, i.pkey)

            tar_gz_file = tarfile_path.split("/")[-1]
            path = host_dict_list[i.id]["path"]
            ssh.put_file(tarfile_path, f'{path}/{tar_gz_file}')
            file_name = tar_gz_file.split(".tar.gz")[0]
            command = f'cd {path} && tar xf {path}/{tar_gz_file} &&cp -Rf {file_name}/* . && rm -rf {file_name} {tar_gz_file}'
            command += ' &&SPUG_DST_DIR=$(pwd)'

            # 忽略

            # 运行后
            if host_dict_list[i.id]["script_text"]:
                for script_cmd in host_dict_list[i.id]["script_text"].splitlines():
                    if not script_cmd:
                        continue
                    command += f" &&{script_cmd}"

            command += '&& echo "deploy success"'
            for code, out in ssh.exec_command_with_stream(command):
                print(code, out)
            if code != 0:
                # error
                return f"Deploy Err {out}"

        return
