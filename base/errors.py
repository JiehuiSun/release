# 定义BaseError，其它所有错误类都继承BaseError
# 设定对应的errno和errmsg
# 正常使用时，raise MethodError就可以抛出相应的异常
# 但是有时候这里定义的errmsg可能不适合所有场景，
# 那么可以通过传入自定义的errmsg来更改
# raise MethodError('别瞎调用我接口')
class BaseError(Exception):
    errno = 10000
    errmsg = '程序员跑路了'

    def __init__(self, errmsg=None):
        if errmsg:
            self.errmsg = errmsg


class MethodError(BaseError):
    errno = 10002
    errmsg = '不支持的请求方式'


class InvalidArgsError(BaseError):
    errno = 10003
    errmsg = '无效的参数'


class LoginError(BaseError):
    errno = 11001
    errmsg = '用户名或密码错误'


class LogoutError(BaseError):
    errno = 11002
    errmsg = '用户名或密码错误'


class LoginExpiredError(BaseError):
    errno = 40801
    errmsg = '登录状态已过期，请重新登录'


class TokenError(BaseError):
    errno = 40801
    errmsg = '非法请求'


class NoTokenError(BaseError):
    errno = 40801
    errmsg = '请求header中缺少token'


class ParamsError(BaseError):
    errno = 10001
    errmsg = '请求参数异常'

class DBError(BaseError):
    errno = 99999
    errmsg = '数据库异常'
