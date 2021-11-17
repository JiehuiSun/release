#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# Create: 2021-11-17 15:19:38
# Author: huihui - sunjiehuimail@foxmail.com
# Filename: host_service.py

from sqlalchemy import or_
from base import db
from models.models import Hosts, HostProject
from . import handle_page, magic_key


class HostServer():
    """
    主机服务器
    """
    @classmethod
    def add_host(cls, name, hostname, port, username, pkey, desc, user_id):
        host_dict = {
            "name": name,
            "hostname": hostname,
            "port": port,
            "username": username,
            "pkey": pkey,
            "desc": desc,
            "created_by_id": user_id,
            "is_verified": True
        }

        host_obj = Hosts(**host_dict)
        db.session.add(host_obj)
        db.session.commit()

        return

    @classmethod
    def del_host(cls, id):
        try:
            host_obj = Hosts.query.get(id)
        except Exception as e:
            raise f"删除失败, {str(e)}"

        host_obj.is_deleted = True
        db.session.commit()

        return

    @classmethod
    def update_host(cls, id, name=None, hostname=None, port=None,
                    username=None, pkey=None, desc=None, user_id=None):
        try:
            host_obj = Hosts.query.get(id)
        except Exception as e:
            raise f"更新失败, 主机信息不存在或已被删除, {str(e)}"

        if name:
            host_obj.name = name
        if hostname:
            host_obj.hostname = hostname
        if port:
            host_obj.port = port
        if username:
            host_obj.username = username
        if pkey:
            try:
                pkey_str = magic_key.decrypt(pkey.encode())
                pkey = pkey_str
            except:
                pass
            host_obj.pkey = pkey
        if desc:
            host_obj.desc = desc
        if user_id:
            # TODO 不依赖spug后应设置更新字段
            host_obj.created_by_id = user_id

        db.session.commit()
        return

    @classmethod
    def list_host(cls, keyword=None, page_num=1, page_size=999):
        host_obj_list = Hosts.query.filter_by(is_deleted=False)
        host_obj_list = host_obj_list.order_by(Hosts.id.desc())
        if keyword:
            host_obj_list = host_obj_list.filter(
                or_(
                    Hosts.name.like(f"%{keyword}%"),
                    Hosts.hostname.like(f"%{keyword}%"),
                    Hosts.desc.like(f"%{keyword}%"),
                )
            )

        count = host_obj_list.count()
        host_obj_list = handle_page(host_obj_list, page_num, page_size)

        host_list = list()
        for i in host_obj_list:
            host_dict = i.to_dict()
            # 列表不展示私钥
            host_dict.pop("pkey")
            # host_dict["pkey"] = magic_key.encrypt(host_dict["pkey"]).decode()

        ret = {
            "data_list": host_list,
            "count": count
        }

        return ret

    @classmethod
    def query_host(cls, id):
        try:
            host_obj = Hosts.query.get(id)
        except Exception as e:
            raise f"查询失败, 主机信息不存在或已被删除, {str(e)}"

        ret = host_obj.to_dict()
        ret["pkey"] = ret.encrypt(ret["pkey"]).decode()

        return ret
