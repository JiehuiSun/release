#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# Create: 2021-11-13 19:35:07
# Author: huihui - sunjiehuimail@foxmail.com
# Filename: deploy_service.py


from models.models import Host, HostProject
from services.ssh_service import SSH


class Deploy():
    """
    部署
    """
    @classmethod
    def add_deploy(cls, project_id, tarfile_path):
        host_project_obj_list = HostProject.query.filter_by(project_id=project_id,
                                                            is_deleted=False).all()

        host_id_list = [i.host_id for i in host_project_obj_list]

        host_obj_list = Host.query.filter(Host.id.in_(host_id_list)).all()

        for i in host_obj_list:
            ssh = SSH(i.hostname, i.port, i.username, i.pkey)

            tar_gz_file = tarfile_path.split("/")[-1]
            ssh.put_file(tarfile_path, f'/tmp/{tar_gz_file}')
            command = f'cd /tmp && tar xf {tar_gz_file} && echo "deploy success"'
            for code, out in ssh.exec_command_with_stream(command):
                pass
            if code != 0:
                # error
                return f"Deploy Err {out}"

        return
