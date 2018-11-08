from datetime import datetime

from django_redis import get_redis_connection
from rest_framework import status
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin, CreateModelMixin
from rest_framework.viewsets import GenericViewSet
from rest_framework.generics import GenericAPIView, CreateAPIView, RetrieveAPIView, UpdateAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework_jwt.settings import api_settings
from rest_framework_jwt.views import ObtainJSONWebToken, jwt_response_payload_handler

from cart.utils import merge_cart_cookie_to_redis
from goods.models import Goods, SKU
from goods.serializer import SKUSerializer
from users import constants
from users.models import User, Address
from users.serializer import CreateUserSerializer, UserDetailSerializer, UserEmailSerializer, UserAddressSerializer, \
    AddressTitleSerializer, BrowsHistorySerializer


# 用户浏览记录增加及展示API
class BrowseHistoryView(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BrowsHistorySerializer

    # 新增用户浏览记录API POST /browse_histories/
    # def post(self, request):
    #     """
    #     登录用户的浏览记录
    #     1.获取商品sku_id并校验（sku_id必传 sku_id对应商品是否存在）
    #     2.在redis中存储用户浏览商品的sku_id
    #     3.返回响应 sku_id
    #     :return:
    #     """
    #     serializer = self.get_serializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save()
    #     return Response(serializer.data)

    # 展示用户浏览记录API
    def get(self, request):
        """
        登录用户浏览记录获取
        1.从redis中获取用户浏览的商品sku_id
        2.根据sku_id获取对应商品的数据
        3.将商品数据序列化返回
        :return:
        """
        redis_coon = get_redis_connection('history')
        skus_id_list = redis_coon.lrange('history_%s' % self.request.user.id, 0, -1)
        skus_list = []
        for sku_id in skus_id_list:
            skus_list.append(SKU.objects.get(id=sku_id))
        serializer = SKUSerializer(skus_list, many=True)
        return Response(serializer.data)


# 验证用户名是否已注册API GET /usernames/(?P<username>\w{5,20})/count/
class UsernameCountView(APIView):
    # def get(self, request, username):
    #     count = User.objects.filter(username__exact=username).count()
    #     # return Response({'message': '用户名已注册'})
    #     data = {
    #         'username': username,
    #         'count': count
    #     }
    #     return Response(data)
    def get(self, request, username):
        count = User.objects.filter(username__exact=username).count()
        legal = 1
        if username.isdigit():
            legal = 0
        return Response({
            'count': count,
            'legal': legal
        }, status=status.HTTP_200_OK)


# 验证手机号码是否已注册APIGET /mobiles/(?P<mobile>1[3-9]\d{9})/count/
class MobileCountView(APIView):
    # def get(self, request, mobile):
    #     count = User.objects.filter(mobile__exact=mobile).count()
    #     data = {
    #         'mobile': mobile,
    #         'count': count
    #     }
    #     return Response(data)
    def get(self, request, mobile):
        count = User.objects.filter(mobile__exact=mobile).count()
        return Response({
            'count': count
        }, status=status.HTTP_200_OK)


# 用户注册信息提交API POST /users/
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


# 用户中心信息显示API GET /user/
class UserDetailView(RetrieveAPIView):
    # 设置权限等级
    permission_classes = [IsAuthenticated]
    # 设置序列化器类
    serializer_class = UserDetailSerializer

    # 重写父类get_object方法
    def get_object(self):
        return self.request.user

        # # def get(self, request):
        # #     """
        # #     获取登录用户基本信息：
        # #     1.获取登录用户user
        # #     2.将用户数据序列化返回
        # #     :return:
        # #     """
        # #
        # #     # user = request.user
        # #     user = self.get_object()
        # #     serializer = self.get_serializer(user)
        # #     return Response(serializer.data)


# 设置登录用户邮箱API PUT /email/
class EmailView(UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserEmailSerializer

    def get_object(self):
        return self.request.user
        #
        # def put(self, request):
        #     """
        #     1.获取登录用户user
        #     2.获取email并校验 参数完整性 格式
        #     3.设置登录用户的邮箱并给邮箱发送一封验证邮件
        #     4.返回应答 邮箱设置成功
        #     :return:
        #     """
        #     user = self.get_object()
        #     serializer = self.get_serializer(user, data=request.data)
        #     serializer.is_valid(raise_exception=True)
        #     serializer.save()


# 用户邮箱验证API PUT /emails/verification/?token=<token>
class EmailVerifyView(GenericAPIView):
    def put(self, request):
        """
        1.获取token并进行校验 token必传 token是否有效
        2.设置对应用户的邮箱验证标记email_active
        3.返回应答 验证成功
        """
        token = request.query_params.get('token')
        if not token:
            return Response({'data': '未获取到token值'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.check_verify_email_token(token)
        if not user:
            return Response({'data': '无效的token值'}, status=status.HTTP_400_BAD_REQUEST)
        user.email_active = True
        user.save()

        return Response({'data': 'OK'})


# 收货地址API
class UserAddressViewSet(UpdateModelMixin, CreateModelMixin, GenericViewSet):
    # serializer_class = UserAddressSerializer
    # permission_classes = [IsAuthenticated]
    #
    # def get_queryset(self):
    #     queryset = self.request.user.addresses.filter(is_delete=False)
    #     return queryset
    #
    # def list(self):
    #     queryset = self.get_queryset()
    #     serializer = self.get_serializer(queryset, many=True)
    #     user = self.request.user
    #     return Response({
    #         'addresses': serializer.data,
    #         'user_id': user.id,
    #     })
    #
    # def create(self, request, *args, **kwargs):
    #     # 判断用户设置收获地址数目是否超出限制
    #     count = self.request.user.addresses.filter(is_delete=False).count()
    #     if count >= constants.USER_MAX_ADDRESS_COUNT:
    #         return Response({'message': '用户收获地址数目已达上限'})
    #     return super().create(request, *args, **kwargs)
    #
    # # 收货地址逻辑删除 DELETE /address/pk/
    # def destroy(self, request, *args, **kwargs):
    #     address = self.get_object()
    #     address.is_delete = True
    #     address.save()
    #     return Response(status=status.HTTP_204_NO_CONTENT)
    #
    # # 设置默认收获地址 PUT /address/pk/status
    # @action(methods=['PUT'], detail=True)
    # def status(self, request, pk=None):
    #     address = self.get_object()
    #     self.request.user.default_address = address
    #     address.save()
    #     return Response({'message': '设置默认收货地址成功'}, status=status.HTTP_200_OK)

    permission_classes = [IsAuthenticated]
    serializer_class = UserAddressSerializer

    # 重写Update方法的get_queryset方法 返回查询集为用户的所有收获地址
    def get_queryset(self):
        return self.request.user.addresses.filter(is_delete=False)

    # 查询收货地址 GET /addresses/
    # def get(self, request):
    def list(self, request, *args, **kwargs):
        # addresses = request.user.addresses.filter(is_delete=False)
        addresses = self.get_queryset()
        serializer = self.get_serializer(addresses, many=True)
        user = self.request.user
        default_address_id = request.user.default_address_id

        return Response({
            'addresses': serializer.data,
            'default_address_id': default_address_id,
            'limit': constants.USER_MAX_ADDRESS_COUNT,
            'user_id': user.id
        })

    # 新增地址 POST /addresses/
    def create(self, request, *args, **kwargs):
        count = self.request.user.addresses.count()
        if count >= constants.USER_MAX_ADDRESS_COUNT:
            return Response({'data': '收货地址设置已达上限'}, status=status.HTTP_400_BAD_REQUEST)
        return super(UserAddressViewSet, self).create(request, *args, **kwargs)

    # 删除地址 DELETE /addresses/<pk>/
    # def delete(self, request, pk, *args, **kwargs):
    def destory(self, request, pk, *args, **kwargs):
        address = request.user.addresses.get(pk=pk)
        address.is_delete = True
        address.save()
        return Response({'data': '地址删除成功'}, status=status.HTTP_204_NO_CONTENT)

    # 设置默认地址 PUT /addresses/<pk>/status/
    @action(methods=['PUT'], detail=True)
    def status(self, request, pk, *args, **kwargs):
        # user = request.user
        # # 用户默认地址与地址类之间为1对1的关系 故可直接设置
        # user.Address = request.user.addresses.get(pk=pk)
        # user.save()

        # 使用GenericAPIView种的方法进行优化
        address = self.get_object()
        request.user.default_address = address
        request.user.save()
        return Response({'data': 'OK'}, status=status.HTTP_200_OK)

    # 设置地址标题 PUT /addresses/<pk>/title/
    @action(methods=['PUT'], detail=True)
    def title(self, request, pk, *args, **kwargs):
        # address = request.user.addresses.get(pk=pk)
        # address.title = request.data.get('title')

        # 调用GenericAPIView的方法并使用序列化器进行优化
        address = self.get_object()
        serializer = AddressTitleSerializer(instance=address, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


# 重写用户登录API 在登录前合并购物车
class UserAuthorizeView(ObtainJSONWebToken):
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            user = serializer.object.get('user') or request.user
            token = serializer.object.get('token')
            response_data = jwt_response_payload_handler(token, user, request)
            response = Response(response_data)
            if api_settings.JWT_AUTH_COOKIE:
                expiration = (datetime.utcnow() +
                              api_settings.JWT_EXPIRATION_DELTA)
                response.set_cookie(api_settings.JWT_AUTH_COOKIE,
                                    token,
                                    expires=expiration,
                                    httponly=True)
            # 调用合并购物车记录的函数
            merge_cart_cookie_to_redis(request, response, user)
            return response

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
