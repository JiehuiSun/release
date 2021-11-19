#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# Create: 2021-11-17 15:19:38
# Author: huihui - sunjiehuimail@foxmail.com
# Filename: host_service.py

from sqlalchemy import or_
from base import db
from models.models import Hosts, HostProject
from . import handle_page, magic_key
from .user_service import User
from .project_service import Project
from base.errors import ParamsError
from utils import query_operate_ids
from utils.time_utils import datetime_2_str_by_format


class HostServer():
    """
    主机服务器
    """
    @classmethod
    def add_host(cls, name, hostname, username, pkey, user_id, port=22, desc=None):
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
            raise ParamsError(f"删除失败, {str(e)}")

        host_obj.is_deleted = True
        db.session.commit()

        return

    @classmethod
    def update_host(cls, id, name=None, hostname=None, port=None,
                    username=None, pkey=None, desc=None, user_id=None):
        try:
            host_obj = Hosts.query.get(id)
        except Exception as e:
            raise ParamsError(f"更新失败, 主机信息不存在或已被删除, {str(e)}")

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
    def list_host(cls, keyword=None, page_num=1, page_size=999, is_base=False):
        # host_obj_list = Hosts.query.filter_by(is_deleted=False)
        host_obj_list = Hosts.query
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
        user_id_list = list()
        for i in host_obj_list:
            host_dict = i.to_dict()
            # 列表不展示私钥
            host_dict.pop("pkey")
            # host_dict["pkey"] = magic_key.encrypt(host_dict["pkey"]).decode()
            host_list.append(host_dict)
            user_id_list.append(host_dict["created_by_id"])

        if is_base:
            ret = {
                "data_list": host_list,
                "count": count
            }

            return ret

        user_data = User.list_user(user_id_list=user_id_list)
        user_dict_list = dict()
        for i in user_data["data_list"]:
            if i["id"] in user_dict_list:
                continue
            user_dict_list[i["id"]] = {
                "id": i["id"],
                "name": i["name"]
            }

        for i in host_list:
            user_dict = user_dict_list.get(i["created_by_id"])
            if not user_dict:
                user_dict = {
                    "id": 0,
                    "name": "未知"
                }
            i["operator"] = user_dict

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
            raise ParamsError(f"查询失败, 主机信息不存在或已被删除, {str(e)}")

        if not host_obj:
            raise ParamsError("查询失败, 主机信息不存在或已被删除")

        ret = host_obj.to_dict()
        ret["pkey"] = magic_key.encrypt(ret["pkey"]).decode()

        return ret


class ProjectHost():
    """
    项目主机
    """
    @classmethod
    def add_host(cls, name, host_id_list: list, project_id, path, env, is_add=True,
                 service_path=None, ignore_text=None, script_text=None, user_id=None):
        host_project_obj = HostProject.query.filter_by(is_deleted=False,
                                                       project_id=project_id).all()
        if host_project_obj and is_add:
            raise ParamsError("该仓库项目已配置主机信息, 可去编辑")

        tmp_dict = {
            "name": name,
            "project_id": project_id,
            "path": path,
            "env": env
        }
        if service_path:
            tmp_dict["service_path"] = service_path
        if ignore_text:
            tmp_dict["ignore_text"] = ignore_text
        if script_text:
            tmp_dict["script_text"] = script_text
        if user_id:
            tmp_dict["created_by_id"] = user_id

        for i in host_id_list:
            tmp_dict["host_id"] = i
            a_obj = HostProject(**tmp_dict)
            db.session.add(a_obj)

        db.session.commit()

        return

    @classmethod
    def update_host(cls, project_id, name=None, host_id_list: list=[],
                    path=None, env=None, service_path=None,
                    ignore_text=None, script_text=None, user_id=None):
        hp_obj = HostProject.query.filter_by(project_id=project_id,
                                             is_deleted=False).all()

        old_id_list = [i.host_id for i in hp_obj]

        id_data = query_operate_ids(old_id_list, host_id_list)
        # del
        if id_data["del_id_list"]:
            for i in id_data["del_id_list"]:
                cls.del_host(project_id, i)

        # add
        if id_data["add_id_list"]:
            tmp_dict = {
                "name": name,
                "project_id": project_id,
                "path": path,
                "env": env,
                "host_id_list": id_data["add_id_list"],
                "is_add": False
            }
            if service_path:
                tmp_dict["service_path"] = service_path
            if ignore_text:
                tmp_dict["ignore_text"] = ignore_text
            if script_text:
                tmp_dict["script_text"] = script_text
            if user_id:
                tmp_dict["user_id"] = user_id
            cls.add_host(**tmp_dict)

        # change
        need_update_id_list = list(set(old_id_list) & set(host_id_list))
        for i in need_update_id_list:
            hp_add_obj = HostProject.query.filter_by(is_deleted=False,
                                                     project_id=project_id,
                                                     host_id=i).one_or_none()
            if not hp_add_obj:
                continue

            if name:
                hp_add_obj.name = name
            if path:
                hp_add_obj.path = path
            if env:
                hp_add_obj.env = env
            if service_path:
                hp_add_obj.service_path = service_path
            if ignore_text:
                hp_add_obj.ignore_text = ignore_text
            if script_text:
                hp_add_obj.script_text = script_text
            if user_id:
                hp_add_obj.created_by_id = user_id

        db.session.commit()

        return

    @classmethod
    def del_host(cls, project_id, host_id=None):
        """
        根据项目ID跟主机ID做唯一处理(不做批量)
        """
        hp_obj = HostProject.query.filter_by(project_id=project_id,
                                             is_deleted=False)
        if host_id:
            hp_obj = hp_obj.filter_by(host_id=host_id)

        if hp_obj:
            hp_obj.update({"is_deleted": True}, synchronize_session=False)
            db.session.commit()

        return

    @classmethod
    def list_host(cls, keyword=None, page_num=None, page_size=None):
        params_d = {
            "need_git_info": False
        }
        if keyword:
            params_d["keyword"] = keyword
        if page_num:
            params_d["page_num"] = page_num
        if page_size:
            params_d["page_size"] = page_size
        project_data = Project.list_project(**params_d)

        project_id_list = [i["id"] for i in project_data["data_list"]]
        tmp_obj_list = HostProject.query.filter_by(is_deleted=False) \
            .filter(HostProject.project_id.in_(project_id_list))

        tmp_dict = dict()
        host_id_list = list()
        for i in tmp_obj_list:
            host_id_list.append(i.host_id)
            if i.project_id not in tmp_dict:
                tmp_dict[i.project_id] = {
                    "hp_name": i.name,
                    "host_id_list": [i.host_id],
                    "hp_env": i.env,
                    "hp_dt_updated": datetime_2_str_by_format(i.dt_updated),
                    "host_list": []
                }
            else:
                tmp_dict[i.project_id]["host_id_list"].append(i.host_id)

        host_data = HostServer.list_host(is_base=True)
        host_dict_list = dict()
        for i in host_data["data_list"]:
            host_dict_list[i["id"]] = i

        for i in project_data["data_list"]:
            hp_dict = tmp_dict.get(i["id"], {})
            if hp_dict:
                i.update(hp_dict)

            for x in i.get("host_id_list", []):
                host_dict = host_dict_list.get(x)
                if host_dict:
                    i["host_list"].append(host_dict)
        return project_data

    @classmethod
    def query_host(cls, project_id):
        try:
            project_id = int(project_id)
        except:
            raise ParamsError("非法请求")

        hp_obj_list = HostProject.query.filter_by(project_id=project_id,
                                                  is_deleted=False).all()
        if not hp_obj_list:
            ret = {
                "name": "",
                "project_id": project_id,
                "host_id_list": [],
                "path": "",
                "service_path": "",
                "ignore_text": "",
                "script_text": "",
                "env": "",
                "dt_created": "",
            }
        else:
            host_id_list = [i.host_id for i in hp_obj_list]
            ret = hp_obj_list[0].to_dict()
            ret["host_id_list"] = host_id_list

        return ret
