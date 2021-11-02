#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# Create: 2021-10-21 19:26:54
# Author: huihui - sunjiehuimail@foxmail.com
# Filename: requirement_service.py


from base import db
from base.errors import ParamsError, InvalidArgsError, DBError
from models.models import (RequirementModel, RequirementProjectModel, RequirementCodeModel,
                           REQUIREMENT_FLOW_STATUS, REQUIREMENT_FLOW_DICT)
from . import handle_page


class Requirement():
    """
    需求
    """
    @classmethod
    def add_requirement(cls, name, desc=None, status_code=None, delayed=None,
                        dt_plan_started=None, dt_plan_deved=None,
                        dt_plan_tested=None, dt_plan_released=None,
                        dt_plan_finished=None, project_user_id_list=None,
                        product_user_id_list=None, web_user_id_list=None,
                        api_user_id_list=None, test_user_id_list=None):
        """
        新增需求(基本信息)
        """
        requirement_dict = {
            "name": name,
        }

        if desc:
            requirement_dict["desc"] = desc
        if status_code:
            requirement_dict["status_code"] = status_code
        if delayed:
            requirement_dict["delayed"] = delayed
        if dt_plan_started:
            requirement_dict["dt_plan_started"] = dt_plan_started
        if dt_plan_deved:
            requirement_dict["dt_plan_deved"] = dt_plan_deved
        if dt_plan_tested:
            requirement_dict["dt_plan_tested"] = dt_plan_tested
        if dt_plan_released:
            requirement_dict["dt_plan_released"] = dt_plan_released
        if dt_plan_finished:
            requirement_dict["dt_plan_finished"] = dt_plan_finished
        if dt_plan_finished:
            requirement_dict["project_user_ids"] = ",".join(str(i) for i in project_user_id_list)
        if dt_plan_finished:
            requirement_dict["product_user_ids"] = ",".join(str(i) for i in product_user_id_list)
        if dt_plan_finished:
            requirement_dict["web_user_ids"] = ",".join(str(i) for i in web_user_id_list)
        if dt_plan_finished:
            requirement_dict["api_user_ids"] = ",".join(str(i) for i in api_user_id_list)
        if dt_plan_finished:
            requirement_dict["test_user_ids"] = ",".join(str(i) for i in test_user_id_list)

        requirement = RequirementModel(**requirement_dict)

        db.session.add(requirement)
        db.session.commit()

        return

    @classmethod
    def list_requirement(cls, type_id=None, keyword=None, status_id=None,
                         page_num=1, page_size=999):
        """
        需求列表

        TODO 时间筛选的机制有点多，流程确认好后再增加

        TODO type_id应该分几个层级，根据不同层级筛选不同节点的时间, 目前先用固定值做配置与筛选
        """
        requirement_obj_list = RequirementModel.query.filter_by(is_deleted=False)
        if status_id:
            code_list = dict(REQUIREMENT_FLOW_STATUS)[status_id]
            requirement_obj_list = requirement_obj_list.filter(RequirementModel.status_code.in_(code_list))

        if type_id:
            requirement_obj_list = requirement_obj_list.filter_by(type_id=type_id)
        if keyword:
            requirement_obj_list = requirement_obj_list.filter(RequirementModel.name.like(f"%{keyword}%"))

        count = requirement_obj_list.count()
        requirement_obj_list = handle_page(requirement_obj_list, page_num, page_size)

        requirement_list = list()
        for i in requirement_obj_list:
            r_dict = i.to_dict()
            requirement_list.append(i.to_dict())

        ret = {
            "data_list": requirement_list,
            "count": count
        }
        return ret

    @classmethod
    def query_requirement(cls, requirement_id):
        try:
            requirement_obj = RequirementModel.query.get(requirement_id)
            if requirement_obj.is_deleted:
                raise ParamsError("Requirement Not Exist or Use Delete")
        except Exception as e:
            raise ParamsError("Requirement Not Exist or Use Delete")

        requirement_dict = requirement_obj.to_dict()

        user_id_list = requirement_dict["all_user_id_list"]
        return requirement_dict

    @classmethod
    def del_requirement(cls, id):
        try:
            requirement_obj = RequirementModel.query.get(id)
            requirement_obj.is_deleted = True
            db.session.commit()
        except Exception as e:
            raise ParamsError("Requirement Not Exist or Use Delete")

    @classmethod
    def update_requirement_status(cls, id, status_id):
        """
        更新需求状态
        """
        pass


class RequirementGroup():
    """
    需求关联组
    """
    @classmethod
    def update_group(cls, requirement_id, type_id, group_list: list):
        """
        更新需求关联组
        """
        if not group_list:
            raise ParamsError("'group_list' Is Required")

        # TODO 先取道该需求的该类型的所有组，然后拿到所有组ID，跟新的组ID计算，根据差异做增/删
        try:
            for i in group_list:
                if not isinstance(i, dict):
                    raise ParamsError(f"'{i}' Params Error")

                project_obj = Project.query_project(i["project_id"], False)

                d = {
                    "requirement_id": requirement_id,
                    "type_id": type_id,
                    "project_id": i["project_id"],
                    "group_id": project_obj.group_id,
                    "branch": i["branch"],
                    "comment": i["comment"],
                    "user_ids": ",".join(str(x) for x in i["user_id_list"]),
                    "is_auto_deploy": True if i["is_auto_deploy"] else False
                }
                r_g = RequirementProjectModel(**d)
                db.session.add(r_g)
                db.session.flush()
        except Exception as e:
            db.session.rollback()
            raise InvalidArgsError(str(e))
        db.session.commit()

        return

    @classmethod
    def list_group(cls, requirement_id, type_id=None):
        """
        获取需求组的列表
        """
        group_obj_list = RequirementProjectModel.query.filter_by(requirement_id=requirement_id,
                                                                 is_deleted=False)

        if type_id:
            group_obj_list = group_obj_list.filter_by(type_id=type_id)

        group_obj_list = group_obj_list.all()

        group_list = list()

        for i in group_obj_list:
            group_list.append(i.to_dict())

        return group_list


class RequirementProject():
    """
    需求项目
    """
    @classmethod
    def list_project(cls, requirement_id, type_id=None):
        project_obj_list = RequirementProjectModel.query.filter_by(requirement_id=requirement_id,
                                                                   is_deleted=False)

        if type_id:
            project_obj_list = project_obj_list.filter_by(type_id=type_id)

        project_obj_list = project_obj_list.all()

        project_list = list()

        for i in project_obj_list:
            project_list.append(i.to_dict())

        return project_list
