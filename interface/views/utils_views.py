#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# Create: 2021-11-05 18:42:35
# Author: huihui - sunjiehuimail@foxmail.com
# Filename: utils_views.py


from flask import make_response, send_file, current_app

from api import Api
from base.errors import ParamsError


class DownLoadView(Api):
    """
    下载
    """
    def list(self):
        self.params_dict = {
            "file": "required str",
        }

        self.ver_params()
        file_name = self.data["file"]
        repository_dir = current_app.config["REPOSITORY_DIR"]
        file_name = f"{repository_dir}/{file_name}"
        try:
            resp = make_response(send_file(file_name))
            resp.headers["Content-Disposition"] = f'attachment; filename={file_name.split("/")[-1]}'
            resp.headers['Content-Type'] = 'application/zip'
        except Exception as e:
            print(str(e))
            raise ParamsError(f"文件下载失败, {str(e)}")
        return resp
