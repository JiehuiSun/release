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
    def add_deploy(cls, project_id, tarfile_path):
        host_project_obj_list = HostProject.query.filter_by(project_id=project_id,
                                                            is_deleted=False).all()

        host_dict_list = dict()
        for i in host_project_obj_list:
            host_dict_list[i.host_id] = i.path

        host_obj_list = Hosts.query.filter(Hosts.id.in_(list(host_dict_list.keys()))).all()
        if not host_obj_list:
            # 未配置主机信息
            raise "未配置主机信息"

        for i in host_obj_list:
            ssh = SSH(i.hostname, i.port, i.username, i.pkey)

            tar_gz_file = tarfile_path.split("/")[-1]
            print(host_dict_list[i.id])
            ssh.put_file(tarfile_path, f'{host_dict_list[i.id]}/{tar_gz_file}')
            command = f'cd {host_dict_list[i.id]} && tar xf {host_dict_list[i.id]}/{tar_gz_file} && echo "deploy success"'
            for code, out in ssh.exec_command_with_stream(command):
                print(code, out)
            if code != 0:
                # error
                return f"Deploy Err {out}"

        return
