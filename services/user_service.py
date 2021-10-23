#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# Create: 2021-10-20 16:47:04
# Author: huihui - sunjiehuimail@foxmail.com
# Filename: user_service.py


from base import db
from models.models import DevUserModel, GroupModel


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
                   group_id_list: list = []):
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

        count = group_obj_list.count()
        group_obj_list = group_obj_list.all()

        group_list = list()
        for i in group_obj_list:
            group_list.append(i.to_dict())

        ret = {
            "data_list": group_list,
            "count": count
        }
        return ret
