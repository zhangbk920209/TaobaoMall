# 重写jwt_response_payload_handler方法, 在token的基础上添加返回id及username
import re
from django.contrib.auth.backends import ModelBackend

from users.models import User


def jwt_response_payload_handler(token, user=None, request=None):
    return {
        'user_id': user.id,
        'username': user.username,
        'token': token
    }


# 封装获取用户函数
def get_user_by_account(account):
    """
    根据帐号获取user对象
    :param account: 账号，可以是用户名，也可以是手机号
    :return: User对象 或者 None
    """
    # 判断帐号是否为手机号
    try:
        if re.match(r'1[3-9]\d{9}$', account):
            # 根据手机号查找用户
            user = User.objects.get(mobile=account)
        else:
            user = User.objects.get(username=account)
    except User.DoesNotExist:
        return None
    else:
        return user


# jwt中的obtain_jwt_token视图中登录验证使用的是django框架认证后端类Backend中的authenticate方法
# 重写该方法以支持手机号登录 而后修改配置选项中认证后端类为自定义
class UsernameMobileAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        user = get_user_by_account(username)
        if user is not None and user.check_password(password):
            return user
