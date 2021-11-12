from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from utils.flask_redis import FlaskRedis
from utils.session import Session
from flask_mail import Mail
from flask_apscheduler import APScheduler
# from flask_ldap3_login import LDAP3LoginManager
from flask_simpleldap import LDAP


db = SQLAlchemy()
redis = FlaskRedis()
session = Session()
lm = LoginManager()
mail = Mail()
apscheduler = APScheduler()
# ldap_manager = LDAP3LoginManager()
ldap_manager = LDAP()


class DefaultConfig(object):

    DEBUG = True
    SECRET_KEY = '4e4y>;8i~O=+d8?8!1DTB)Vs9VJiX$<<Dt@~]R_,@Q;tIqk?csY(+YT;V)dU~j=.'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://base:base@localhost/base?charset=utf8mb4'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    REDIS_URI = 'redis://:@localhost:6379/3'
    APP_LOGIN_AUTH_KEY = "mumway"
    WEB_LOGIN_AUTH_KEY = "mumway"

    MODULES = (
        "account",
        "interface",
        "model",
    )

    BABEL_DEFAULT_LOCALE = "zh_CN"

    # gitlab
    GITLAB_TOKEN = ""
    GITLAB_HOST = ""
    GIT_ABS_CMD = "/usr/bin/git"

    REPOSITORY_DIR = ""
    DOWNLOAD_HOST = ""

    # Ldap
    LDAP_HOST = ""
    LDAP_PORT= 389
    LDAP_BASE_DN = ""
    LDAP_USERNAME = ""
    LDAP_PASSWORD = ""
    LDAP_OPENLDAP = True
    LDAP_USER_OBJECT_FILTER = ""

    TOKEN_DURATION = 3600 * 48

# local_configs目的: 因为线上、测试、开发环境的配置不同，
# 所以每个环境可以有自己的local_configs来覆盖configs里的DefaultConfig
# 但是这里有一个问题


try:
    from .local_configs import *
except ModuleNotFoundError as e:
    pass
