import os
import logging
import time
import datetime
from flask import Flask
from werkzeug.routing import BaseConverter
from flask_cors import CORS
from flask import request
from flask import jsonify

from base import configs
from base import db
from base import redis
from base import session
from base import mail
from base import apscheduler
from base import tasks
from base import ldap_manager
# from base import tasks_queue
from account.helpers import algorithm_auth_login


APP_NAME = 'base'

class RegexConverter(BaseConverter):
    def __init__(self, url_map, *args):
        super(RegexConverter, self).__init__(url_map)
        # 将接受的第1个参数当作匹配规则进行保存
        self.regex = args[0]


def create_app():
    app = Flask(APP_NAME)
    app.config.from_object(configs.DefaultConfig)
    app.url_map.converters['re'] = RegexConverter
    config_blueprint(app)
    config_logger(app)
    config_db(app)
    config_redis(app)
    config_session(app)
    config_login(app)
    config_mail(app)
    # config_apscheduler(app)
    config_ldap(app)
    CORS(app, supports_credentials=True)
    return app


def config_blueprint(app):
    from base.urls import instance
    app.register_blueprint(instance, url_prefix='/api')


def config_logger(app):
    log_dir = '../logs/'
    log_filename = 'redbullLog.log'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    config_dict = {
        'filename': log_dir + log_filename,
        'format': '%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
    }
    logging.basicConfig(**config_dict)


def config_db(app):
    db.init_app(app)


def config_redis(app):
    redis.init_app(app)


def config_session(app):
    session.init_app(app)


def config_login(app):
    configs.lm.init_app(app)

    from account.models.UserModel import UserModel

    @configs.lm.request_loader
    def load_user_from_request(req):
        auth_token = req.headers.get('token')
        if not auth_token:
            return
        try:
            user_id, random_str, timestamp, auth_code = auth_token.split("|")
        except Exception as e:
            return
        auth_code_new = algorithm_auth_login(user_id, random_str, timestamp)
        if auth_code == auth_code_new.split("|")[-1]:
            ret = UserModel.query.filter_by(id=user_id).one_or_none()
            # user_session = {"user_id": user_id}
        else:
            return
        if not ret:
            return
        return ret


def config_mail(app):
    mail.init_app(app)


def config_apscheduler(app):
    apscheduler.init_app(app)
    apscheduler.start()


def config_ldap(app):
    ldap_manager.init_app(app)


app = create_app()
tasks.InitTasks()


@app.route("/utils/upload_file/", endpoint="/utils/upload_file/", methods=['POST'])
def upload_file():
    if request.method == 'POST':
        appid = request.headers.get("App-Id")
        if not appid or appid not in app.config["ALLOW_APPID"]:
            res = {
                "errmsg": "非法请求",
                "errcode": 10000
            }
            return jsonify(res)

        f = request.files['file']
        new_file_name = "{0}_{1}{2}{3}".format(
            f.filename.split(".")[0],
            str(datetime.datetime.now()).split()[0].replace("-", ""),
            str(int(time.time()))[5:],
            f.filename.replace(f.filename.split(".")[0], "")
        )

        dir = request.form.get("dir")
        if dir not in app.config["ALLOW_FILE_DIR"]:
            res = {
                "errmsg": "目录未授权",
                "errcode": 10000
            }
            return jsonify(res)

        data_dir = f"{app.config['REPOSITORY_DIR']}/data"
        if not os.path.exists(data_dir):
            os.system(f"mkdir {data_dir}")
        file_dir = f"{data_dir}/{dir}"
        if not os.path.exists(file_dir):
            for i in dir.split("/"):
                if not os.path.exists(f"{data_dir}/{i}"):
                    os.system(f"mkdir {data_dir}/{i}")
                data_dir += f"/{i}"

        f.save(os.path.join(file_dir, new_file_name))

        file_path = f"data/{dir}/{new_file_name}"
        res = {
            "errmsg": "上传成功",
            "errcode": 0,
            "data": {
                "file_path": file_path,
                "download_url": "{0}{1}?file={2}".format(
                    app.config["DOWNLOAD_HOST"],
                    "/api/interface/v1/utils/download/",
                    file_path
                )
            }
        }
        return jsonify(res)
    else:
        res = {
            "errmsg": "非法请求",
            "errcode": 10000
        }
        return jsonify(res)
