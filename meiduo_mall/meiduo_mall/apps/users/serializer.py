import re
from django_redis import get_redis_connection
from rest_framework import serializers

from goods.models import SKU
from users import constants
from users.models import User, Address


# 历史浏览记录序列化器类
class BrowsHistorySerializer(serializers.Serializer):
    sku_id = serializers.IntegerField(label='商品SKU编号', min_value=1)

    # 校验商品是否存在
    def validate_sku_id(self, value):
        try:
            sku = SKU.objects.get(id=value)
        except SKU.DoesNotExist:
            raise serializers.ValidationError('商品不存在')
        return value

    # 在redis中存储用户浏览商品的sku_id
    def create(self, validated_data):
        user_id = self.context['request'].user.id
        sku_id = validated_data['sku_id']
        redis_coon = get_redis_connection('history')
        # 创建管道
        pl = redis_coon.pipeline()
        # 删除已存在的商品浏览记录 0 表示只要全部删除
        pl.lrem('history_%s' % user_id, 0, sku_id)
        # 添加新的浏览记录
        pl.lpush('history_%s' % user_id, sku_id)
        # 保存最多5条记录
        pl.ltrim('history_%s' % user_id, 0, constants.USER_BROWSING_HISTORY_COUNTS_LIMIT - 1)

        pl.execute()

        return validated_data


# 注册序列化器
class CreateUserSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(label='重复密码', write_only=True)
    sms_code = serializers.CharField(label='短信验证码', write_only=True)
    allow = serializers.CharField(label='同意协议', write_only=True)
    token = serializers.CharField(label='jswtoken', read_only=True)

    class Meta:
        model = User
        fields = ('id', 'token', 'username', 'password', 'password2', 'mobile', 'allow', 'sms_code')
        extra_kwargs = {
            'username': {
                'max_length': 20,
                'min_length': 5,
                'error_messages': {
                    'man_length': '仅允许5-20个字符的帐号',
                    'mix_length': '仅允许5-20个字符的帐号',
                }
            },
            'password': {
                'write_only': True,
                'max_length': 20,
                'min_length': 8,
                'error_messages': {
                    'min_length': '仅允许8-20个字符的密码',
                    'max_length': '仅允许8-20个字符的密码',
                }
            },
        }

    def validate_mobile(self, value):
        if not re.match('1[3-9]\d{9}', value):
            raise serializers.ValidationError('手机格式错误')
        count = User.objects.filter(mobile=value).count()
        if count > 0:
            raise serializers.ValidationError('手机号已被注册')
        return value

    def validate_allow(self, value):
        print(value)
        if value != 'true':
            raise serializers.ValidationError('请勾选同意协议')
        return value

    def validate(self, attrs):
        print(attrs)
        # 验证两次密码是否相同
        password = attrs['password']
        password2 = attrs['password2']
        if password != password2:
            raise serializers.ValidationError('两次密码不一致')
        # 验证短信验证码
        sms_code = attrs['sms_code']
        redis_coon = get_redis_connection('verify_codes')
        mobile = attrs['mobile']
        real_sms_code = redis_coon.get('sms_%s' % mobile)
        if not real_sms_code:
            raise serializers.ValidationError('短信验证码已过期')
        if real_sms_code.decode() != sms_code:
            raise serializers.ValidationError('短信验证码错误')
        return attrs

    def create(self, validated_data):
        del validated_data['allow']
        del validated_data['sms_code']
        del validated_data['password2']
        # 调用
        user = User.objects.create_user(**validated_data)
        # user = super().create(validated_data)
        # # 调用django的认证系统加密密码
        # user.set_password(validated_data['password'])
        # user.save()

        from rest_framework_jwt.settings import api_settings
        # 创建组织payload载荷的方法
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        # 创建生成jwt token数据的方法
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        # 传入用户对象 生成载荷数据
        payload = jwt_payload_handler(user)
        # 传入载荷 生成token数据
        token = jwt_encode_handler(payload)

        user.token = token

        return user


# 用户个人信息序列化器
class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'email_active', 'mobile')


# 登录用户设置邮箱序列化器
class UserEmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email')
        extra_kwargs = {
            'email': {
                'required': True
            }
        }

    def update(self, instance, validated_data):
        # 修改用户邮箱地址
        email = validated_data['email']  # email格式在User类中自动进行验证
        instance.email = email
        instance.save()

        # 调用User类生成链接地址方法
        verify_url = instance.generate_verify_rul()
        # 开启Celery异步任务发送邮件
        from celery_tasks.email.tasks import send_verify_email
        send_verify_email.delay(email, verify_url)
        return instance


# 用户地址序列化器
class UserAddressSerializer(serializers.ModelSerializer):
    province = serializers.StringRelatedField(read_only=True)
    city = serializers.StringRelatedField(read_only=True)
    district = serializers.StringRelatedField(read_only=True)
    province_id = serializers.IntegerField(label='省ID', required=True)
    city_id = serializers.IntegerField(label='市ID', required=True)
    district_id = serializers.IntegerField(label='区ID', required=True)

    class Meta:
        model = Address
        exclude = ('user', 'is_delete', 'create_time', 'update_time')

    # 验证手机号
    def validate_mobile(self, value):
        if not re.match(r'1[3-9]\d{9}$', value):
            raise serializers.ValidationError('手机号码格式错误')
        return value

    # 新建地址
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


# 地址标题序列化器
class AddressTitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ('title',)
