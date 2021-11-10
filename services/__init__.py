#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# Create: 2021-10-20 16:46:29
# Author: huihui - sunjiehuimail@foxmail.com
# Filename: __init__.py


import time
import datetime


def handle_page(query_obj_list, page_num, page_size):
    """
    分页处理

    params: query_obj_list query对象
    """
    query_obj_list = query_obj_list.limit(page_size) \
                                   .offset((page_num - 1) * page_size).all()

    return query_obj_list


def calculate_page(total_count, page_size=10):
    """
    计算分页
    """
    page_count = (page_size + total_count - 1) // page_size

    return page_count


def gen_version_num(name, count_num, env, branch):
    """
    生成版本号
    """
    version_num = "{0}-{1}-{2}{3}-{4}-{5}".format(
        count_num,
        env,
        str(datetime.datetime.now()).split()[0].replace("-", ""),
        str(int(time.time()))[5:],
        name,
        branch
    )
    return version_num
