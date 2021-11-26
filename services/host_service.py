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
        host_obj_list = Hosts.query.all()
        host_id_list = dict()
        for i in host_obj_list:
            tmp_name = f"{i.hostname}|{i.username}"
            if tmp_name not in host_id_list:
                host_id_list[tmp_name] = i.id

        host_obj_list = Hosts.query.filter(Hosts.id.in_(list(host_id_list.values())))
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
                                                       project_id=project_id,
                                                       env=env).all()
        if host_project_obj and is_add:
            raise ParamsError(f"该仓库项目的{env}环境已配置主机信息, 可去编辑")

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
                    path=None, env=None, service_path=None, id=None,
                    ignore_text=None, script_text=None, user_id=None):
        if not id:
            raise ParamsError("修改配置未更新至最新版")

        hp_obj = HostProject.query.get(id)
        if not hp_obj:
            raise ParamsError("该配置不存在或已删除")

        hp_obj = HostProject.query.filter_by(project_id=hp_obj.project_id,
                                             env=hp_obj.env,
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
        hp_update_obj_list = HostProject.query \
            .filter(HostProject.id.in_(need_update_id_list)).all()
        for i in hp_update_obj_list:
            if name:
                i.name = name
            if path:
                i.path = path
            if env:
                i.env = env
            if service_path:
                i.service_path = service_path
            if ignore_text:
                i.ignore_text = ignore_text
            if script_text:
                i.script_text = script_text
            if user_id:
                i.created_by_id = user_id

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
    def list_host(cls, keyword=None, page_num=None, page_size=None,
                  project_keyword=None, host_keyword=None, env=None):

        project_id_list = dict()
        host_id_list = list()

        host_obj_list = HostProject.query.filter_by(is_deleted=False)
        if env:
            host_obj_list = host_obj_list.filter_by(env=env).all()
        if keyword:
            host_obj_list = host_obj_list.filter(HostProject.name.like(f"%{keyword}%"))
        host_obj_list = host_obj_list.all()

        h_list = dict()
        h_id_list = list()
        h_dict_list = dict()
        for i in host_obj_list:
            tmp_n = f"{i.project_id}|{i.env}"
            if tmp_n not in h_list:
                h_list[tmp_n] = [i.host_id]
                h_dict_list[tmp_n] = [i.to_dict()]
                h_id_list.append(i.id)
            else:
                h_list[tmp_n].append(i.host_id)
                h_dict_list[tmp_n].append(i.to_dict())

        if project_keyword:
            params_d = {
                "need_git_info": False,
                "keyword": project_keyword
            }
            project_data = Project.list_project(**params_d)
            for i in project_data["data_list"]:
                if i["id"] not in project_id_list:
                    project_id_list[i["id"]] = i

        if host_keyword:
            params_d = {
                "is_base": True,
                "keyword": host_keyword
            }
            host_data = HostServer.list_host(**params_d)
            host_id_list = [i["id"] for i in host_data["data_list"]]

        host_obj_list = HostProject.query.filter_by(is_deleted=False) \
            .filter(HostProject.id.in_(h_id_list))
        if keyword:
            host_obj_list = host_obj_list.filter(HostProject.name.like(f"%{keyword}%"))

        if project_id_list:
            host_obj_list = host_obj_list \
            .filter(HostProject.project_id.in_(list(project_id_list.keys())))

        if host_id_list:
            host_obj_list = host_obj_list \
            .filter(HostProject.host_id.in_(host_id_list))

        count = host_obj_list.count()

        host_obj_list = handle_page(host_obj_list, page_num, page_size)

        ret_list = list()
        host_id_list = list()
        for i in host_obj_list:
            tmp_dict = {
                "hp_id": i.id,
                "hp_name": i.name,
                "host_id_list": h_list.get(f"{i.project_id}|{i.env}", []),
                "hp_env": i.env,
                "hp_dt_updated": datetime_2_str_by_format(i.dt_updated),
                "host_list": h_dict_list.get(f"{i.project_id}|{i.env}", []),
                "project_id": i.project_id,
            }

            project_dict = project_id_list.get(i.project_id)
            if project_dict:
                tmp_dict["name"] = project_dict["name"]
                tmp_dict["desc"] = project_dict["desc"]

            ret_list.append(tmp_dict)

        ret = {
            "data_list": ret_list,
            "count": count
        }

        return ret

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
                "host_list": []
            }
        else:
            host_id_list = [i.host_id for i in hp_obj_list]
            ret = hp_obj_list[0].to_dict()
            ret["host_id_list"] = host_id_list
            ret["host_list"] = list()

        host_data = HostServer.list_host(is_base=True)
        host_dict_list = dict()
        for i in host_data["data_list"]:
            host_dict_list[i["id"]] = i

        for x in ret["host_id_list"]:
            host_dict = host_dict_list.get(x)
            if host_dict:
                ret["host_list"].append(host_dict)
        return ret
