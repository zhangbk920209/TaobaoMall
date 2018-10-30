from rest_framework import status
from rest_framework.generics import GenericAPIView, CreateAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from users.models import User
from users.serializer import CreateUserSerializer, UserDataSerializer


# GET /usernames/(?P<username>\w{5,20})/count/
class UsernameCountView(APIView):
    def get(self, request, username):
        count = User.objects.filter(username__exact=username).count()
        # return Response({'message': '用户名已注册'})
        data = {
            'username': username,
            'count': count
        }
        return Response(data)


# GET /mobiles/(?P<mobile>1[3-9]\d{9})/count/
class MobileCountView(APIView):
    def get(self, request, mobile):
        count = User.objects.filter(mobile__exact=mobile).count()
        data = {
            'mobile': mobile,
            'count': count
        }
        return Response(data)


# POST /users/
class UsersView(CreateAPIView):
    serializer_class = CreateUserSerializer
    #
    # def post(self, request):
    #     """
    #     注册用户信息的保存:
    #     1. 接收参数并进行校验(参数完整性，两次密码是否一致，手机号格式，手机号是否注册，短信验证码是否正确，是否同意协议)
    #     2. 创建新用户并保存注册用户的信息
    #     3. 返回应答，注册成功
    #     """
    #     serializer = self.get_serializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save()
    #     return Response(serializer.data, status=status.HTTP_201_CREATED)


# GET /user/
class UserDetailView(RetrieveAPIView):
    # 设置权限等级
    permission_classes = [IsAuthenticated]
    # 设置序列化器类
    serializer_class = UserDataSerializer

    # 重写父类get_object方法
    def get_object(self):
        return self.request.user

    # def get(self, request):
    #     """
    #     获取登录用户基本信息：
    #     1.获取登录用户user
    #     2.将用户数据序列化返回
    #     :return:
    #     """
    #
    #     # user = request.user
    #     user = self.get_object()
    #     serializer = self.get_serializer(user)
    #     return Response(serializer.data)


