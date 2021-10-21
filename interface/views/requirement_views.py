#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# Create: 2021-10-13 16:00:45
# Author: huihui - sunjiehuimail@foxmail.com
# Filename: requirement_views.py


from api import Api


class RequirementViews(Api):
    """
    需求
    """
    def list(self):
        self.params_dict = {
            "type_id": "optional str",
            "status_id": "optional str",
        }

        self.ver_params()

        requirement_list = list()

        for i in range(2):
            requirement_dict = {
                "id": i + 1,
                "name": f"需求{i + 1}",
                "desc": f"需求{i + 1}的简介",
                "dt_plan_started": "2021-10-10 12:12:12",
                "dt_plan_deved": "2021-10-10 12:12:12",
                "dt_plan_tested": "2021-10-10 12:12:12",
                "dt_plan_released": "2021-10-10 12:12:12",
                "dt_plan_finished": "2021-10-10 12:12:12",
                "dt_finished": "2021-10-10 12:12:12",
                "group": [
                    {
                        "id": f"{i + 1}",
                        "value": f"组名{i + 1}",
                    },
                ],
                "status": {
                    "id": self.data.get("status_id", 1),
                    "name": "状态名"
                }
            }
            requirement_list.append(requirement_dict)

        ret = {
            "data_list": requirement_list
        }

        return self.ret(data=ret)

    def get(self):
        self.params_dict = {
        }

        self.ver_params()

        requirement_dict = {
            "id": self.key,
            "name": "需求名name",
            "desc": "简介desc(需求名称+jira地址)",
            "dt_plan_deved": "2021-10-10 12:12:12",
            "dt_deved": "2021-10-10 12:12:12",
            "dt_plan_tested": "2021-10-10 12:12:12",
            "dt_tested": "2021-10-10 12:12:12",
            "dt_plan_released": "2021-10-10 12:12:12",
            "dt_released": "2021-10-10 12:12:12",
            "dt_plan_finished": "2021-10-10 12:12:12",
            "dt_finished": "2021-10-10 12:12:12",
        }

        return self.ret(data=requirement_dict)


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

        group_list = list()

        for i in range(2):
            group_dict = {
                "id": i + 1,
                "name": f"需求{i + 1}",
                "project_id": 1,
                "branch": "分支",
                "user_list": [
                    {"id": 1, "name": "User1"},
                    {"id": 2, "name": "User2"},
                ],
                "comment": "备注"
            }
            group_list.append(group_dict)

        ret = {
            "data_list": group_list
        }

        return self.ret(data=ret)
