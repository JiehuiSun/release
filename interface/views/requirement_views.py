#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# Create: 2021-10-13 16:00:45
# Author: huihui - sunjiehuimail@foxmail.com
# Filename: requirement_views.py


from api import Api
from base.errors import ParamsError

from services import calculate_page
from services.user_service import Group, User
from services.requirement_service import (Requirement, RequirementGroup,
                                          RequirementProject, RequirementStatusFlow,
                                          RequirementStatus)


class RequirementViews(Api):
    """
    需求
    """
    def list(self):
        """
        type_id 是左侧的类型(所有项目/待研发/延期)
        status_id 是顶部的状态(待研发/研发中/测试中/已上线)

        细品的话这两个状态确实不一样或者说使用上不一样或者更便捷
        """
        self.params_dict = {
            "type_id": "optional str",
            "status_id": "optional str",
            "keyword": "optional str",
            "page_num": "optional str",
            "page_size": "optional str"
        }

        self.ver_params()

        self.handle_page_params()

        requirement_data = Requirement.list_requirement(**self.data)

        requirement_list = requirement_data["data_list"]

        # 可优化
        for i in requirement_list:
            if i["all_user_id_list"]:
                group_data = Group.list_group(user_id_list=i["all_user_id_list"])
                i["group"] = group_data["data_list"]
            else:
                i["group"] = []

            # 状态流处理
            next_status = RequirementStatusFlow.get_next_status(i.get("status_code", 0))
            i["next_status_code"] = next_status["next_status_code"]
            i["next_status_name"] = next_status["next_status_name"]

        ret = {
            "data_list": requirement_list,
            "count": requirement_data["count"],
            "page_num": self.data["page_num"],
            "page_size": self.data["page_size"],
            "page_count": calculate_page(requirement_data["count"])
        }

        return self.ret(data=ret)

    def get(self):
        self.params_dict = {
        }

        self.ver_params()

        requirement_dict = Requirement.query_requirement(self.key)

        return self.ret(data=requirement_dict)

    def post(self):
        self.params_dict = {
            "name": "required str",
            "desc": "optional str",
            "status_code": "optional int",
            "delayed": "optional str",
            "dt_plan_started": "optional str",
            "dt_plan_deved": "optional str",
            "dt_plan_tested": "optional str",
            "dt_plan_released": "optional str",
            "dt_plan_finished": "optional str",
            "project_user_id_list": "optional list",
            "product_user_id_list": "optional list",
            "web_user_id_list": "optional list",
            "api_user_id_list": "optional list",
            "test_user_id_list": "optional list",
            "test_env": "optional str"
        }

        self.ver_params()

        try:
            Requirement.add_requirement(**self.data)
        except Exception as e:
            return self.ret(errcode=100000, errmsg=str(e))

        return self.ret()

    def delete(self):
        self.params_dict = {
            "id": "required int"
        }

        self.ver_params()

        Requirement.del_requirement(**self.data)

        return self.ret()

    def put(self):
        self.params_dict = {
            "id": "required int",
            "name": "required str",
            "desc": "optional str",
            "status_code": "optional int",
            "delayed": "optional str",
            "dt_plan_started": "optional str",
            "dt_plan_deved": "optional str",
            "dt_plan_tested": "optional str",
            "dt_plan_released": "optional str",
            "dt_plan_finished": "optional str",
            "project_user_id_list": "optional list",
            "product_user_id_list": "optional list",
            "web_user_id_list": "optional list",
            "api_user_id_list": "optional list",
            "test_user_id_list": "optional list",
        }

        self.ver_params()

        try:
            Requirement.update_requirement(**self.data)
        except Exception as e:
            return self.ret(errcode=100000, errmsg=str(e))

        return self.ret()


class RequirementStatusViews(Api):
    """
    需求
    """
    def put(self):
        self.params_dict = {
            "id": "required int",
            "status_id": "required int",
        }

        self.ver_params()

        Requirement.update_requirement_status(**self.data)

        return self.ret()



class RequirementGroupViews(Api):
    """
    需求关联组
    """
    def list(self):
        self.params_dict = {
            "requirement_id": "required str",
            "type_id": "optional str",
        }

        self.ver_params()

        group_list = RequirementGroup.list_group(**self.data)

        group_id_list = [i["group_id"] for i in group_list]

        group_data = Group.list_group(group_id_list=group_id_list)

        group_dict_list = dict()
        for i in group_data["data_list"]:
            group_dict_list[i["id"]] = i["name"]

        for i in group_list:
            i["group_name"] = group_dict_list.get(i["group_id"])
            user_id_list = i["user_ids"].split(",")
            i["user_list"] = User.list_user(user_id_list=user_id_list)

        ret = {
            "data_list": group_list
        }

        return self.ret(data=ret)

    def put(self):
        self.params_dict = {
            "requirement_id": "required int",
            "type_id": "required int",
            "group_list": "required list",
        }

        self.ver_params()

        self.params_dict = {
            "project_id": "required int",
            "group_id": "optional int",
            "branch": "required str",
            "comment": "optional str",
            "user_id_list": "optional list",
            "is_auto_deploy": "optional pass"
        }

        d = self.data
        group_list = d["group_list"]
        for i in group_list:
            self.data = i
            self.ver_params()

        try:
            RequirementGroup.update_group(**d)
        except Exception as e:
            raise ParamsError(str(e))

        return self.ret()


class RequirementProjectViews(Api):
    """
    需求项目
    """
    def list(self):
        self.params_dict = {
            "requirement_id": "required str",
            "type_id": "optional str"
        }

        self.ver_params()

        project_list = RequirementProject.list_project(**self.data)

        ret = {
            "data_list": project_list
        }

        return self.ret(data=ret)

    def put(self):
        self.params_dict = {
            "requirement_id": "required int",
            "type_id": "required int",
            "project_list": "required list",
        }

        self.ver_params()

        self.params_dict = {
            "project_id": "required int",
            "branch": "required str",
            "comment": "optional str",
            "is_auto_deploy": "optional pass"
        }

        d = self.data
        group_list = d["project_list"]
        for i in group_list:
            self.data = i
            self.ver_params()

        try:
            RequirementProject.update_project(**d)
        except Exception as e:
            raise ParamsError(str(e))

        return self.ret()


class RequirementCodeViews(Api):
    """
    需求状态码

    # TODO 状态码不应该前端传，而是后端自己处理(tmp)
    """
    def put(self):
        self.params_dict = {
            "requirement_id": "required int",
            "status_code": "required int"
        }

        self.ver_params()

        RequirementStatus.update_status(**self.data)

        return self.ret()
