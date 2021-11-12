#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# Create: 2021-10-20 16:47:04
# Author: huihui - sunjiehuimail@foxmail.com
# Filename: user_service.py


import json

from sqlalchemy import or_

from base import db
from models.models import DevUserModel, GroupModel, UserGroupModel, RoleModel, JOB_TYPE
from . import handle_page
from base.errors import ParamsError
from utils import query_operate_ids


class Group():
    """
    组
    """
    @classmethod
    def add_group(cls, name, desc=None, parent_id=None, email=None, type_id=None):
        """
        新增组
        """
        group_dict = {
            "name": name
        }

        if desc:
            group_dict["desc"] = desc
        if parent_id:
            group_dict["parent_id"] = parent_id
        if email:
            group_dict["email"] = email
        if type_id:
            group_dict["type_id"] = type_id

        group = GroupModel(**group_dict)

        db.session.add(group)
        db.session.commit()

        return

    @classmethod
    def list_group(cls, type_id=None, keyword=None, parent_id=None,
                   group_id_list: list = [], page_num=1, page_size=999,
                   user_id_list=None):
        """
        组列表
        """
        group_obj_list = GroupModel.query.filter_by(is_deleted=False)
        if type_id:
            group_obj_list = group_obj_list.filter_by(type_id=type_id)
        if keyword:
            # 暂时区分大小写
            group_obj_list = group_obj_list.filter(GroupModel.name.like(f"%{keyword}%"))
        if parent_id:
            group_obj_list = group_obj_list.filter_by(parent_id=parent_id)

        if group_id_list:
            group_obj_list = group_obj_list.filter(GroupModel.id.in_(group_id_list))

        if user_id_list is not None:
            u_tmp_obj_list = UserGroupModel.query.filter(UserGroupModel.user_id.in_(user_id_list))
            group_id_list = [i.group_id for i in u_tmp_obj_list]
            if group_id_list:
                group_obj_list = group_obj_list.filter(GroupModel.id.in_(group_id_list))

        count = group_obj_list.count()
        group_obj_list = handle_page(group_obj_list, page_num, page_size)

        group_list = list()
        for i in group_obj_list:
            group_list.append(i.to_dict())

        ret = {
            "data_list": group_list,
            "count": count
        }
        return ret


class User():
    """
    用户
    """
    @classmethod
    def list_user(cls, keyword=None, user_id_list: list = [], group_id=None,
                  type_id=None, page_num=1, page_size=999, need_detail=False):
        user_obj_list = DevUserModel.query.filter_by(is_deleted=False)

        if keyword:
            user_obj_list = user_obj_list.filter(or_(DevUserModel.name.like(f"%{keyword}%"),
                                                     DevUserModel.desc.like(f"%{keyword}%")))

        if group_id:
            user_group_obj_list = UserGroupModel.query.filter_by(is_deleted=False,
                                                                 group_id=group_id).all()
            user_id_list = [i.user_id for i in user_group_obj_list]

        if user_id_list:
            user_obj_list = user_obj_list.filter(DevUserModel.id.in_(user_id_list))

        count = user_obj_list.count()
        user_obj_list = handle_page(user_obj_list, page_num, page_size)

        user_list = list()
        for i in user_obj_list:
            user_dict = i.to_dict()
            if user_dict["role_ids"]:
                user_dict["role_id_list"] = user_dict["role_ids"].split(",")
            else:
                user_dict["role_id_list"] = list()
            user_list.append(user_dict)

        if need_detail:
            for i in user_list:
                if i["role_id_list"]:
                    role_obj_list = RoleModel.query.filter(RoleModel.id.in_(i["role_id_list"]))
                    role_list = [j.to_dict() for j in role_obj_list.all()]
                    i["role_list"] = role_list
                else:
                    i["role_list"] = list()

                if i["job"]:
                    try:
                        job_id = int(i["job"])
                    except:
                        job_id = 0
                    i["job"] = {
                        "id": job_id,
                        "name": dict(JOB_TYPE).get(job_id, "")
                    }
                else:
                    i["job"] = dict()

                tmp_obj_list = UserGroupModel.query.filter_by(user_id=i["id"]).all()
                if tmp_obj_list:
                    group_id_list = [j.group_id for j in tmp_obj_list]
                    group_obj_list = GroupModel.query.filter(GroupModel.id.in_(group_id_list)).all()
                    i["group_list"] = [j.to_dict() for j in group_obj_list]
                else:
                    i["group_list"] = list()

        for i in user_list:
            i["name"] = i["desc"]

        ret = {
            "data_list": user_list,
            "count": count
        }

        return ret

    @classmethod
    def query_user(cls, user_id):
        try:
            user_obj = DevUserModel.query.get(user_id)
        except Exception as e:
            raise ParamsError(f"用户查询失败, id: {user_id}, {str(e)}")

        user_dict = user_obj.to_dict()

        # role
        if user_dict["role_ids"]:
            user_dict["role_id_list"] = user_dict["role_ids"].split(",")
        else:
            user_dict["role_id_list"] = list()

        # menu
        menu_list = list()
        if user_dict["role_id_list"]:
            role_data = Role.list_role(id_list=user_dict["role_id_list"])
            for i in role_data["data_list"]:
                menu_list += i["menu_list"]
            menu_list = list(set(menu_list))
        user_dict["menu_list"] = menu_list
        return user_dict

    @classmethod
    def update_user(cls, id, role_id_list: list=[], group_id_list: list=[], job_id=None):
        try:
            user_obj = DevUserModel.query.get(id)
        except Exception as e:
            raise ParamsError("用户查询失败")

        if role_id_list:
            user_obj.role_ids = ",".join(str(i) for i in role_id_list)
        if group_id_list:
            old_group_obj = UserGroupModel.query.filter_by(user_id=id).all()
            old_group_id_list = [i.group_id for i in old_group_obj]
            id_data = query_operate_ids(old_group_id_list, group_id_list)
            if id_data["add_id_list"]:
                for i in id_data["add_id_list"]:
                    tmp_d = {
                        "user_id": id,
                        "group_id": i
                    }
                    g = UserGroupModel(**tmp_d)
                    db.session.add(g)
            if id_data["del_id_list"]:
                tmp_o = UserGroupModel.query.filter(
                    UserGroupModel.user_id.in_(id_data["del_id_list"])
                )
                tmp_o.update({"is_deleted": True}, synchronize_session=False)
        if job_id:
            user_obj.job = job_id

        db.session.commit()

        return


class Role():
    """
    角色
    """
    @classmethod
    def add_role(cls, name, menu_list: list, type_id=1, comment=None):
        role_dict = {
            "name": name,
            "menu_list": json.dumps(menu_list),
            "type_id": type_id
        }
        if comment:
            role_dict["comment"] = comment
        role = RoleModel(**role_dict)

        db.session.add(role)
        db.session.commit()

        return

    @classmethod
    def update_role(cls, id, name=None, menu_list: list=[], type_id=1, comment=None):
        try:
            role_obj = RoleModel.query.get(id)
        except:
            raise ParamsError("角色不存在")

        role_obj.menu_list = json.dumps(menu_list)

        if name != role_obj.name:
            role_obj.name = name
        if type_id != role_obj.type_id:
            role_obj.type_id = type_id
        if comment != role_obj.comment:
            role_obj.comment = comment

        db.session.commit()

        return

    @classmethod
    def list_role(cls, keyword=None, type_id=None, page_num=1, page_size=999, id_list: list=[]):
        role_obj_list = RoleModel.query.filter_by(is_deleted=False) \
            .order_by(RoleModel.id.desc())
        if keyword:
            role_obj_list = role_obj_list.filter(RoleModel.name.like(f"%{keyword}%"))
        if type_id:
            role_obj_list = role_obj_list.filter_by(type_id=type_id)
        if id_list:
            role_obj_list = role_obj_list.filter(RoleModel.id.in_(id_list))

        count = role_obj_list.count()
        role_obj_list = handle_page(role_obj_list, page_num, page_size)

        role_list = list()
        for i in role_obj_list:
            role_list.append(i.to_dict())

        ret = {
            "data_list": role_list,
            "count": count
        }

        return ret

    @classmethod
    def query_role(cls, id):
        try:
            role_obj = RoleModel.query.get(id)
        except:
            raise ParamsError("角色不存在")
        if role_obj.is_deleted:
            raise ParamsError("角色不存在或已被删除")
        return role_obj.to_dict()

    @classmethod
    def del_role(cls, id):
        try:
            role_obj = RoleModel.query.get(id)
        except:
            raise ParamsError("角色不存在")
        role_obj.is_deleted = True
        db.session.commit()
        return

class Job():
    @classmethod
    def list_job(cls):
        ret_list = list()
        for k, v in dict(JOB_TYPE).items():
            ret_list.append({
                "id": k,
                "name": v
            })
        return ret_list
