#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# Create: 2021-10-21 19:26:54
# Author: huihui - sunjiehuimail@foxmail.com
# Filename: requirement_service.py


from base import db
from base.errors import ParamsError, InvalidArgsError, DBError
from models.models import RequirementModel, RequirementProjectModel, RequirementCodeModel


class Requirement():
    """
    需求
    """
    @classmethod
    def add_requirement(cls, name, desc=None, status_code=None, delayed=None,
                        dt_plan_started=None, dt_plan_deved=None,
                        dt_plan_tested=None, dt_plan_released=None,
                        dt_plan_finished=None):
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

        requirement = RequirementModel(**requirement_dict)

        db.session.add(requirement)
        db.session.commit()

        return

    @classmethod
    def list_requirement(cls, type_id=None, keyword=None, status_id=None):
        """
        需求列表

        TODO 时间筛选的机制有点多，流程确认好后再增加

        TODO type_id应该分几个层级，根据不同层级筛选不同节点的时间, 目前先用固定值做配置与筛选
        """
        requirement_obj_list = RequirementModel.query.filter_by(is_deleted=False)
        if status_id:
            status_obj = RequirementCodeModel.query.filter_by(code=status_id).one_or_none()
            if not status_obj:
                raise DBError("Database Requirement Code Error")

            status_id = status_obj.id
            requirement_obj_list = requirement_obj_list.filter_by(status_code=status_id)

        if type_id:
            requirement_obj_list = requirement_obj_list.filter_by(type_id=type_id)
        if keyword:
            requirement_obj_list = requirement_obj_list.filter(RequirementModel.name.like(f"%{keyword}%"))

        count = requirement_obj_list.count()
        requirement_obj_list = requirement_obj_list.all()

        requirement_list = list()
        for i in requirement_obj_list:
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
            if not requirement_obj.is_deleted:
                raise ParamsError("Requirement Not Exist or Use Delete")
        except Exception as e:
            raise ParamsError("Requirement Not Exist or Use Delete")

        return requirement_obj.to_dict()


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

                d = {
                    "requirement_id": requirement_id,
                    "type_id": type_id,
                    "project_id": i["project_id"],
                    "group_id": i["group_id"],
                    "branch": i["branch"],
                    "comment": i["comment"]
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