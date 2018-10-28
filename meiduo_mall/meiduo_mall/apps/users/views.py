from rest_framework import status
from rest_framework.generics import GenericAPIView, CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from users.models import User
from users.serializer import CreateUserSerializer


# 判断用户名是否被注册接口
# GET /usernames/(?P<username>\w{5,20})/count/
class UsernameCountView(APIView):
    def get(self, request, username):
        count = User.objects.filter(username=username).count()
        # return Response({'message': '用户名已注册'})
        data = {
            'username': username,
            'count': count
        }
        return Response(data)


# GET /mobiles/(?P<mobile>1[3-9]\d{9})/count/
class MobileCountView(APIView):
    def get(self, request, mobile):
        count = User.objects.filter(mobile=mobile).count()
        data = {
            'mobile': mobile,
            'count': count
        }
        return Response(data)


# POST /users/
class UsersView(CreateAPIView):
    serializer_class = CreateUserSerializer

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
