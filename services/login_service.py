#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# Create: 2021-11-11 15:11:13
# Author: huihui - sunjiehuimail@foxmail.com
# Filename: login_service.py



class User():
    @classmethod
    def login(cls, username, password):
        ret = {
            "token": "123",
        }
        return ret

    @classmethod
    def logout(cls):
        return
