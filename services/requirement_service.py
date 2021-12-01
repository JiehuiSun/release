#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# Create: 2021-10-21 19:26:54
# Author: huihui - sunjiehuimail@foxmail.com
# Filename: requirement_service.py


from base import db
from base.errors import ParamsError, InvalidArgsError, DBError
from models.models import (RequirementModel, RequirementProjectModel, RequirementCodeModel,
                           REQUIREMENT_FLOW_STATUS, REQUIREMENT_FLOW_DICT,
                           REQUIREMENT_FLOW_NEXT_DICT)
from . import handle_page
from utils import query_operate_ids, send_ding_errmsg
from utils.time_utils import now_dt
from services.user_service import Group
from services.build_service import BuildLog


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
                        api_user_id_list=None, test_user_id_list=None,
                        test_env="test", leader_user_id_list=None):
        """
        新增需求(基本信息)
        """
        requirement_dict = {
            "name": name,
            "test_env": test_env
        }

        user_id_list = list()
        if desc:
            requirement_dict["desc"] = desc
        if status_code:
            requirement_dict["status_code"] = status_code
            if status_code == 1:
                requirement_dict["dt_started"] = now_dt()
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
        if project_user_id_list:
            requirement_dict["project_user_ids"] = ",".join(str(i) for i in project_user_id_list)
            user_id_list += project_user_id_list
        if product_user_id_list:
            requirement_dict["product_user_ids"] = ",".join(str(i) for i in product_user_id_list)
            user_id_list += product_user_id_list
        if web_user_id_list:
            requirement_dict["web_user_ids"] = ",".join(str(i) for i in web_user_id_list)
            user_id_list += web_user_id_list
        if api_user_id_list:
            requirement_dict["api_user_ids"] = ",".join(str(i) for i in api_user_id_list)
            user_id_list += api_user_id_list
        if test_user_id_list:
            requirement_dict["test_user_ids"] = ",".join(str(i) for i in test_user_id_list)
            user_id_list += test_user_id_list
        if leader_user_id_list:
            requirement_dict["leader_user_ids"] = ",".join(str(i) for i in leader_user_id_list)
            user_id_list += leader_user_id_list

        group_data = Group.list_group(user_id_list=user_id_list)
        group_id_list = [i["id"] for i in group_data["data_list"]]
        requirement_dict["group_ids"] = ",".join(str(i) for i in group_id_list)
        requirement = RequirementModel(**requirement_dict)

        db.session.add(requirement)
        db.session.commit()

        # 直接立项发送消息
        if status_code == 1:
            msg = []
            group_webhook_url_list = []
            title = ""
            group_data = Group.list_group(
                group_id_list=group_id_list,
                type_id=30)
            for x in group_data["data_list"]:
                if x["webhook_url"]:
                    group_webhook_url_list.append(x["webhook_url"])
            title = "项目立项"
            msg.append("#### 恭喜您！已成功立项！")
            msg.append(f"**项目:** {name}")
            msg = {
                "title": title,
                "text": "\n".join(msg)
            }

            RequirementStatus.send_msg(requirement.id, group_webhook_url_list, msg)

        return

    @classmethod
    def list_requirement(cls, type_id=None, keyword=None, status_id=None,
                         page_num=1, page_size=999):
        """
        需求列表

        TODO 时间筛选的机制有点多，流程确认好后再增加

        TODO type_id应该分几个层级，根据不同层级筛选不同节点的时间, 目前先用固定值做配置与筛选
        """
        requirement_obj_list = RequirementModel.query.filter_by(is_deleted=False).order_by(RequirementModel.id.desc())
        if status_id:
            code_list = dict(REQUIREMENT_FLOW_STATUS)[int(status_id)]
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
            requirement_list.append(r_dict)

        ret = {
            "data_list": requirement_list,
            "count": count
        }
        return ret

    @classmethod
    def list_auto_build_requirement(cls, project_id, status_id_le,
                                    status_id_ge, branch):
        req_project_obj_list = RequirementProjectModel.query \
            .filter_by(project_id=project_id,
                       is_deleted=False,
                       branch=branch).all()

        req_project_dict_list = dict()
        for i in req_project_obj_list:
            if i.requirement_id in req_project_dict_list:
                req_project_dict_list[i.requirement_id].append(i)
            else:
                req_project_dict_list[i.requirement_id] = [i]

        if not req_project_dict_list:
            return

        req_obj_list = RequirementModel.query \
            .filter(RequirementModel.status_code >= status_id_le,
                    RequirementModel.status_code <= status_id_ge,
                    RequirementModel.id.in_(list(req_project_dict_list.keys()))).all()

        if not req_obj_list:
            return

        ret_list = list()
        for i in req_obj_list:
            ret_dict = dict()
            if i.status_code == 604:
                ret_dict["env"] = "pre"
            elif i.status_code - 600 < 10:
                ret_dict["env"] = i.test_env or "test"
            else:
                continue

            for x in req_project_dict_list[i.id]:
                ret_dict["project_id"] = x.project_id
                ret_list.append(ret_dict)

        return ret_list


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

    @classmethod
    def update_requirement(cls, id, name=None, desc=None, status_code=None, delayed=None,
                           dt_plan_started=None, dt_plan_deved=None,
                           dt_plan_tested=None, dt_plan_released=None,
                           dt_plan_finished=None, project_user_id_list=None,
                           product_user_id_list=None, web_user_id_list=None,
                           api_user_id_list=None, test_user_id_list=None,
                           test_env="test", leader_user_id_list=None):
        """
        更新需求(基本信息)
        """
        try:
            requirement_obj = RequirementModel.query.get(id)
        except Exception as e:
            raise ParamsError(f"Update Err! ID Not Exist or Use Delete! {str(e)}")

        if name and name != requirement_obj.name:
            requirement_obj.name = name
        if desc and desc != requirement_obj.desc:
            requirement_obj.desc = desc
        if delayed and delayed != requirement_obj.delayed:
            requirement_obj.delayed = delayed
        if status_code and status_code < 10:
            requirement_obj.status_code = status_code
        if dt_plan_started:
            requirement_obj.dt_plan_started = dt_plan_started
        if dt_plan_deved:
            requirement_obj.dt_plan_deved = dt_plan_deved
        if dt_plan_tested:
            requirement_obj.dt_plan_tested = dt_plan_tested
        if dt_plan_released:
            requirement_obj.dt_plan_released = dt_plan_released
        if dt_plan_finished:
            requirement_obj.dt_plan_finished = dt_plan_finished

        if project_user_id_list is not None:
            requirement_obj.project_user_ids = ",".join(str(i) for i in project_user_id_list)
        if product_user_id_list is not None:
            requirement_obj.product_user_ids = ",".join(str(i) for i in product_user_id_list)
        if api_user_id_list is not None:
            requirement_obj.api_user_ids = ",".join(str(i) for i in api_user_id_list)
        if web_user_id_list is not None:
            requirement_obj.web_user_ids = ",".join(str(i) for i in web_user_id_list)
        if test_user_id_list is not None:
            requirement_obj.test_user_ids = ",".join(str(i) for i in test_user_id_list)
        if leader_user_id_list is not None:
            requirement_obj.leader_user_ids = ",".join(str(i) for i in leader_user_id_list)

        user_id_list = list()
        user_id_list += project_user_id_list
        user_id_list += product_user_id_list
        user_id_list += api_user_id_list
        user_id_list += web_user_id_list
        user_id_list += test_user_id_list
        user_id_list += leader_user_id_list

        group_data = Group.list_group(user_id_list=user_id_list)
        group_id_list = [i["id"] for i in group_data["data_list"]]
        requirement_obj.group_ids = ",".join(str(i) for i in group_id_list)

        requirement_obj.test_env = test_env

        db.session.commit()

        return


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

    @classmethod
    def update_project(cls, requirement_id, type_id, project_list: list):
        project_obj_list = RequirementProjectModel.query.filter_by(requirement_id=requirement_id,
                                                                   is_deleted=False,
                                                                   type_id=type_id).all()
        if not project_obj_list:
            for i in project_list:
                i["requirement_id"] = requirement_id
                i["type_id"] = type_id
            cls.add_project(project_list)

            return
        old_id_list = [i.project_id for i in project_obj_list]
        new_id_list = [i["project_id"] for i in project_list]

        id_data = query_operate_ids(old_id_list, new_id_list)
        if id_data["add_id_list"]:
            need_add_list = list()
            for i in project_list:
                if i["project_id"] in id_data["add_id_list"]:
                    i["requirement_id"] = requirement_id
                    i["type_id"] = type_id
                    need_add_list.append(i)
            cls.add_project(need_add_list)

        if id_data["del_id_list"]:
            need_del_list = list()
            for i in project_obj_list:
                if i.project_id in id_data["del_id_list"]:
                    need_del_list.append(i.id)
            cls.del_project(need_del_list)

        return


    @classmethod
    def add_project(cls, data_list: list):
        # 批量添加
        for i in data_list:
            i["is_auto_deploy"] = True if i.get("is_auto_deploy") else False
            o = RequirementProjectModel(**i)
            db.session.add(o)
        db.session.commit()

        return

    @classmethod
    def del_project(cls, id_list: list):
        # 批量软删除
        project_obj_list = RequirementProjectModel.query.filter(
            RequirementProjectModel.id.in_(id_list)
        )
        project_obj_list.update({"is_deleted": True}, synchronize_session=False)
        db.session.commit()

        return


class RequirementStatusFlow():
    """
    需求状态流

    # TODO 临时写死
    """
    @classmethod
    def get_next_status(cls, status_code):
        """
        TODO 为便于扩展, 应该循环状态流取状态节点，利用一样状态流的展示取下一个
        """

        """
        # TODO 临时不用真实流程
        i = dict()
        if not status_code or status_code in (0, 2):
            i["next_status_code"] = 1
            i["next_status_name"] = "立项"
        elif status_code == 1:
            i["next_status_code"] = 401
            i["next_status_name"] = "进入开发"

        if i:
            return i

        for x in REQUIREMENT_FLOW_DICT:
            if status_code == x[0]:
                index_n = REQUIREMENT_FLOW_DICT.index(x)
                if index_n < len(REQUIREMENT_FLOW_DICT) - 1:
                    next_index = index_n + 1
                else:
                    next_index = index_n
                i["next_status_code"] = REQUIREMENT_FLOW_DICT[next_index][0]
                i["next_status_name"] = dict(REQUIREMENT_FLOW_NEXT_DICT)[i["next_status_code"]]
                return i
        return i
        """
        i = dict()
        if not status_code or status_code in (0, 2):
            i["next_status_code"] = 1
            i["next_status_name"] = "立项"
        elif status_code == 1:
            i["next_status_code"] = 402
            i["next_status_name"] = "进入开发"
        elif status_code < 601:
            i["next_status_code"] = 602
            i["next_status_name"] = "提测"
        elif status_code == 602:
            i["next_status_code"] = 604
            i["next_status_name"] = "进入Pre环境"
        elif status_code == 604:
            i["next_status_code"] = 801
            i["next_status_name"] = "申请上线"
        elif status_code == 605:
            i["next_status_code"] = 801
            i["next_status_name"] = "申请上线"
        elif status_code == 801:
            i["next_status_code"] = 888
            i["next_status_name"] = "上线"
        elif status_code == 888:
            i["next_status_code"] = 888
            i["next_status_name"] = "上线完成"
        return i



class RequirementStatus():
    @classmethod
    def update_status(cls, requirement_id, status_code):
        """
        更新需求状态
        """
        try:
            requirement_obj = RequirementModel.query.get(requirement_id)
            if status_code not in dict(REQUIREMENT_FLOW_DICT):
                raise ParamsError("Update Status Err! Status Code Err!")
            requirement_obj.status_code = status_code

            # 修改实际时间
            msg = []
            group_webhook_url_list = []
            title = ""

            group_id_list = requirement_obj.group_ids.split(",")
            if status_code == 1:
                group_data = Group.list_group(
                    group_id_list=group_id_list,
                    type_id=30)
                for x in group_data["data_list"]:
                    if x["webhook_url"]:
                        group_webhook_url_list.append(x["webhook_url"])
                requirement_obj.dt_started = now_dt()
                title = "项目立项"
                msg.append("#### 恭喜您！已成功立项！")
                msg.append(f"**项目:** {requirement_obj.name}")
            elif status_code == 402:
                group_data = Group.list_group(
                    group_id_list=group_id_list,
                    type_id_list=(10, 20))
                for x in group_data["data_list"]:
                    if x["webhook_url"]:
                        group_webhook_url_list.append(x["webhook_url"])
                requirement_obj.dt_deved = now_dt()
                title = "来活了"
                msg.append("#### 来活了")
                msg.append(f"**项目:** {requirement_obj.name}")
                msg.append("###### 小伙伴们, 撸起袖子加油干吧!")
            elif status_code == 602:
                req_project_list = RequirementProject.list_project(requirement_id)
                if not req_project_list:
                    raise ParamsError(f"请配置提测仓库")
                requirement_obj.dt_tested = now_dt()
                title = "申请提测"
                msg.append("#### 申请提测")
                msg.append(f"**项目:** {requirement_obj.name}")
                msg.append("\n**环境:** test")
                group_data = Group.list_group(
                    group_id_list=group_id_list,
                    type_id=40)
                for x in group_data["data_list"]:
                    if x["webhook_url"]:
                        group_webhook_url_list.append(x["webhook_url"])

                # 自动构建
                for i in req_project_list:
                    project_id = i["project_id"]
                    branch = i["branch"]
                # 构建
                BuildLog.add_build_log(project_id, branch, requirement_obj.test_env, user_id=9999)
            elif status_code == 604:
                requirement_obj.dt_released = now_dt()
                title = "进入pre环境"
                msg.append("#### 进入pre环境")
                msg.append(f"**项目:** {requirement_obj.name}")
                group_data = Group.list_group(
                    group_id_list=group_id_list,
                    type_id_list=(10, 20))
                for x in group_data["data_list"]:
                    if x["webhook_url"]:
                        group_webhook_url_list.append(x["webhook_url"])

                # 自动构建
                req_project_list = RequirementProject.list_project(requirement_id)
                for i in req_project_list:
                    project_id = i["project_id"]
                    branch = i["branch"]
                # 构建
                BuildLog.add_build_log(project_id, branch, "pre", user_id=9999)
            elif status_code == 605:
                requirement_obj.dt_released = now_dt()
                title = "已封板"
                msg.append("#### 已封板")
                msg.append(f"**项目:** {requirement_obj.name}")
                group_data = Group.list_group(
                    group_id_list=group_id_list)
                for x in group_data["data_list"]:
                    if x["webhook_url"]:
                        group_webhook_url_list.append(x["webhook_url"])
            elif status_code == 801:
                requirement_obj.dt_finished = now_dt()
                title = "上线申请"
                msg.append("#### 上线申请")
                msg.append(f"**项目:** {requirement_obj.name}")
                group_data = Group.list_group(
                    group_id_list=group_id_list,
                    type_id_list=(10, 20))
                for x in group_data["data_list"]:
                    if x["webhook_url"]:
                        group_webhook_url_list.append(x["webhook_url"])
                # 运维
                ops_group = Group.list_group(type_id=60)
                for x in ops_group["data_list"]:
                    group_webhook_url_list.append(x["webhook_url"])

            db.session.commit()
        except Exception as e:
            raise ParamsError(f"更新状态错误! {str(e)}")

        msg = {
            "title": title,
            "text": "\n".join(msg)
        }
        group_webhook_url_list = list(set(group_webhook_url_list))
        cls.send_msg(requirement_obj.id, group_webhook_url_list, msg)
        return

    @classmethod
    def send_msg(cls, requirement_id, group_webhook_url_list, msg):
        send_ding_errmsg(group_webhook_url_list, msg, msg_type="markdown")
        return
