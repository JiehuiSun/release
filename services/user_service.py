#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# Create: 2021-10-20 16:47:04
# Author: huihui - sunjiehuimail@foxmail.com
# Filename: user_service.py


from base import db
from models.models import DevUserModel, GroupModel, UserGroupModel
from . import handle_page


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
            user_list.append(i.to_dict())
        for i in user_list:
            i["name"] = i["desc"]

        ret = {
            "data_list": user_list,
            "count": count
        }

        return ret
