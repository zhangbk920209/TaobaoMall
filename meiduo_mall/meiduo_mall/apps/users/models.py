from users import constants
from django.contrib.auth.models import AbstractUser
from itsdangerous import TimedJSONWebSignatureSerializer as TJWSSerializer, BadData
from django.conf import settings
from django.db import models
from oauth.models import BaseModel


# 继承DEF框架默认的用户
class User(AbstractUser):
    mobile = models.CharField(max_length=11, unique=True, verbose_name='手机号')
    email_active = models.BooleanField(default=False, verbose_name='验证邮箱')
    default_address = models.ForeignKey('Address', related_name='users', null=True, blank=True, on_delete=models.SET_NULL, verbose_name='默认地址')

    class Meta:
        db_table = 'tb_users'
        verbose_name = '用户'
        verbose_name_plural = verbose_name

    # 生成验证邮箱的url
    def generate_verify_rul(self):
        # 设置地址中要传递的token数据
        data = {
            'user_id': self.id,
            'email': self.email
        }
        # 实例化JWS序列化器对象
        serializer = TJWSSerializer(settings.SECRET_KEY, expires_in=constants.VERIFY_EMAIL_TOKEN_EXPIRES)
        # 使用JWS序列化器对象对数据进行加密, 对获得的bytes数据进行解码
        token = serializer.dumps(data).decode()
        # 拼接接口地址与token数据
        verify_url = " http://www.meiduo.site:8080/success_verify_email.html?token=" + token
        # 返回链接地址
        return verify_url

    @staticmethod
    def check_verify_email_token(token):
        serializer = TJWSSerializer(settings.SECRET_KEY, expires_in=constants.VERIFY_EMAIL_TOKEN_EXPIRES)
        try:
            data = serializer.loads(token)
        except BadData:
            return None
        else:
            user_id = data['user_id']
            email = data['email']
            try:
                user = User.objects.get(id=user_id, email=email)
            except User.DoesNotExist:
                return None
            else:
                return user


# 用户地址模型类
class Address(BaseModel):
    user = models.ForeignKey('User', on_delete=models.CASCADE,related_name='addresses', verbose_name='用户')
    title = models.CharField(max_length=20, verbose_name='地址名称')
    receiver = models.CharField(max_length=20, verbose_name='收货人')
    province = models.ForeignKey('areas.Area', on_delete=models.PROTECT, related_name='province_address', verbose_name='省')
    city = models.ForeignKey('areas.Area', on_delete=models.PROTECT, related_name='city_address', verbose_name='市')
    district = models.ForeignKey('areas.Area', on_delete=models.PROTECT, related_name='district_address', verbose_name='区')
    place = models.CharField(max_length=50, verbose_name='收获地址')
    mobile = models.CharField(max_length=11, verbose_name='手机')
    tel = models.CharField(max_length=20, null=True, blank=True, default='', verbose_name='固定电话')
    email = models.CharField(max_length=30, null=True,blank=True, default='', verbose_name='邮箱')
    is_delete = models.BooleanField(default=False, verbose_name='逻辑删除')

    class Meta:
        db_table = 'tb_address'
        verbose_name = '收货地址'
        verbose_name_plural = verbose_name
        # 地址查询时默认降序
        ordering = ['-update_time']

