#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# Create: 2021-10-20 16:46:29
# Author: huihui - sunjiehuimail@foxmail.com
# Filename: __init__.py


import time
import datetime
# from Cryptodome.Cipher import AES
from Crypto.Cipher import AES
from binascii import b2a_hex, a2b_hex


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




class EncryptDecrypt():
    def __init__(self, key="mumway"):
        self.key = key
        self.mode = AES.MODE_ECB
        self.aes_length = 16
        self.cryptor = AES.new(self.pad_key(self.key).encode(), self.mode)

    # 加密函数，如果text不是16的倍数【加密文本text必须为16的倍数！】，那就补足为16的倍数
    # 加密内容需要长达16位字符，所以进行空格拼接
    def pad(self,text):
        while len(text) % self.aes_length != 0:
            text += ' '
        return text

    # 加密密钥需要长达16位字符，所以进行空格拼接
    def pad_key(self,key):
        while len(key) % self.aes_length != 0:
            key += ' '
        return key

    def encrypt(self, text):

        # 这里密钥key 长度必须为16（AES-128）、24（AES-192）、或32（AES-256）Bytes 长度.目前AES-128足够用
        # 加密的字符需要转换为bytes
        self.ciphertext = self.cryptor.encrypt(self.pad(text).encode())
        # 因为AES加密时候得到的字符串不一定是ascii字符集的，输出到终端或者保存时候可能存在问题
        # 所以这里统一把加密后的字符串转化为16进制字符串
        return b2a_hex(self.ciphertext)

        # 解密后，去掉补足的空格用strip() 去掉

    def decrypt(self, text):
        plain_text = self.cryptor.decrypt(a2b_hex(text)).decode()
        return plain_text.rstrip(' ')

magic_key = EncryptDecrypt()
