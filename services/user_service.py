#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# Create: 2021-10-20 16:47:04
# Author: huihui - sunjiehuimail@foxmail.com
# Filename: user_service.py


import json

from base import db
from models.models import DevUserModel, GroupModel, UserGroupModel, RoleModel
from . import handle_page
from base.errors import ParamsError


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
                  type_id=None, page_num=1, page_size=999):
        user_obj_list = DevUserModel.query.filter_by(is_deleted=False)

        if keyword:
            user_obj_list = user_obj_list.filter(DevUserModel.name.like(f"%{keyword}%"))

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
                user_dict["role_id_list"] = list()
            else:
                user_dict["role_id_list"] = user_dict["role_ids"].split(",")
            user_list.append(user_dict)
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
            raise ParamsError("用户查询失败, id: user_id")

        return user_obj.to_dict()

    @classmethod
    def update_user(cls, id, role_id_list :list=[]):
        try:
            user_obj = DevUserModel.query.get(id)
        except Exception as e:
            raise ParamsError("用户查询失败")

        if role_id_list:
            user_obj.role_ids = ",".join(str(i) for i in role_id_list)

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
    def list_role(cls, keyword=None, type_id=None, page_num=1, page_size=999):
        role_obj_list = RoleModel.query.filter_by(is_deleted=False) \
            .order_by(RoleModel.id.desc())
        if keyword:
            role_obj_list = role_obj_list.filter(RoleModel.name.like(f"%{keyword}%"))
        if type_id:
            role_obj_list = role_obj_list.filter_by(type_id=type_id)

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
