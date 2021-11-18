#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# Create: 2021-11-11 15:11:13
# Author: huihui - sunjiehuimail@foxmail.com
# Filename: login_service.py

import time
import random
import hashlib
from flask import current_app
from flask_login import login_user, current_user, logout_user, login_required

from base import db, redis
from base import ldap_manager
from base.errors import ParamsError
from models.models import DevUserModel
from .user_service import User as user_bke


class User():
    @classmethod
    def login(cls, username, password):

        if not ldap_manager.bind_user(username, password):
            raise ParamsError("登录失败, 用户名或密码错误或未授权, 如没有账户请联系运维开通")

        user_obj = DevUserModel.query.filter_by(is_deleted=False,
                                                name=username).one_or_none()
        if not user_obj:
            user_dict = {
                "nickname": username,
                "name": username,
                "email": f"{username}@xiavan.com",
                "password": cls.gen_pwd(username, password)
            }
            user_obj = DevUserModel(**user_dict)
            db.session.add(user_obj)
            db.session.commit()
        else:
            hash_pwd = cls.gen_pwd(username, password)
            if hash_pwd != user_obj.password:
                user_obj.password = hash_pwd
                db.session.commit()

        token = cls.gen_token(user_obj.id,
                              cls.make_random_str(),
                              int(time.time())
                              )

        # redis
        redis.client.set(token, user_obj.id, current_app.config["TOKEN_DURATION"])

        # TODO 做双层校验需要每次修改用户权限信息等重新登录
        # redis.client.set(f"user_info_{user_obj.id}", user_dict)

        # cookie
        # user_dict = user_bke.query_user(user_obj.id)
        # login_user(user_obj)
        # current_user.token = token

        ret = {
            "token": token,
        }
        return ret

    @classmethod
    def logout(cls):
        # redis.client.delete(current_user.token)
        # logout_user()
        return

    @classmethod
    def gen_token(cls, user_id, random_str, timestamp):
        """
        """
        auth_login_key = current_app.config["WEB_LOGIN_AUTH_KEY"]
        auth_code1 = hashlib.sha256(str("{0}{1}{2}".format(str(user_id), str(random_str), str(auth_login_key))).encode("utf8")).hexdigest()
        auth_code = hashlib.sha256(str("{0}{1}{2}".format(str(auth_code1), str(timestamp), str(auth_login_key))).encode("utf8")).hexdigest()

        ret_params = {
            "user_id": user_id,
            "random_str": random_str,
            "timestamp": timestamp,
            "auth_code": auth_code
        }

        return "{user_id}|{random_str}|{timestamp}|{auth_code}".format(**ret_params)

    @classmethod
    def make_random_str(cls, num=5):
        ret = ''
        for i in range(num):
            num = random.randint(0,9)
            alfa = chr(random.randint(97,122))
            alfa2 = chr(random.randint(65,90))
            s = random.choice([str(num), alfa, alfa2])
            ret = ret+s
        return str(ret)

    @classmethod
    def gen_pwd(cls, username, password):
        auth_login_key = current_app.config["WEB_LOGIN_AUTH_KEY"]
        auth_code = hashlib.sha256(str(username + password + auth_login_key).encode("utf8")).hexdigest()
        return auth_code
