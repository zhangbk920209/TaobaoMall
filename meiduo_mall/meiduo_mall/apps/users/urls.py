from django.conf.urls import url
from users.views import MobileCountView, UsersView
from rest_framework_jwt.views import obtain_jwt_token
from users.views import UsernameCountView

urlpatterns = [
    url(r'^usernames/(?P<username>\w{5,20})/count/$', view=UsernameCountView.as_view()),
    url(r'^mobiles/(?P<mobile>1[3-9]\d{9})/count/$', view=MobileCountView.as_view()),
    url(r'^users/$', view=UsersView.as_view()),
    # 调用jwt扩展包中的登录视图obtain_jwt_token 由视图类ObtainJSONWebToken分发而成
    # 试图类ObtainJSONWebToken继承自JSONWebTokenAPIView, JSONWebTokenAPIView中的post方法使用jwt_response_payload_handler生成响应 响应中仅返回token值
    # jwt_response_payload_handler方法在settings中由JWT_RESPONSE_PAYLOAD_HANDLER进行指定
    # 重写jwt_response_payload_handler方法并修改配置 在登录返回的响应中添加用户信息username及id
    url(r'^authorizations/$', view=obtain_jwt_token)
]
