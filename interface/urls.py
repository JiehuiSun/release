#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# Create: 2021-10-09 18:59:31
# Author: huihui - sunjiehuimail@foxmail.com
# Filename: urls.py


from .views.user_views import GroupView, UserView
from .views.project_views import ProjectView
from .views.requirement_views import (RequirementViews, RequirementGroupViews,
                                      RequirementCodeViews, RequirementProjectViews)
from .views.submit_views import SubmitProjectView
from .views.build_views import BuildProjectView, BuildLogView, BuildConsoleLogView
from .views.gitlab_views import BranchView, SyncProjectView


MODEL_NAME = "interface"

urls = ()

routing_dict = dict()
v1_routing_dict = dict()

# user
v1_routing_dict["group"] = GroupView
v1_routing_dict["user"] = UserView

# project
v1_routing_dict["project"] = ProjectView

# requirement
v1_routing_dict["requirement"] = RequirementViews
v1_routing_dict["requirement_group"] = RequirementGroupViews
v1_routing_dict["requirement_code"] = RequirementCodeViews
v1_routing_dict["requirement_project"] = RequirementProjectViews

# submit
v1_routing_dict["submit_project"] = SubmitProjectView

# build
v1_routing_dict["build_project"] = BuildProjectView
v1_routing_dict["build_log"] = BuildLogView
v1_routing_dict["build_console_log"] = BuildConsoleLogView

# gitlab
v1_routing_dict["gitlab/branch"] = BranchView
v1_routing_dict["gitlab/sync_project"] = SyncProjectView


for k, v in v1_routing_dict.items():
    routing_dict["/v1/{0}/".format(k)] = v
