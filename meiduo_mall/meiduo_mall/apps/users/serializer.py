import re
from rest_framework_jwt.settings import api_settings
from django_redis import get_redis_connection
from rest_framework import serializers
from users.models import User


# 定义注册序列化器
class CreateUserSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(label='重复密码', write_only=True)
    sms_code = serializers.CharField(label='短信验证码', write_only=True)
    allow = serializers.CharField(label='同意协议', write_only=True)

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
        sms_code = attrs['sms_code']
        mobile = attrs['mobile']
        if password != password2:
            raise serializers.ValidationError('两次密码不一致')
        # 验证短信验证码
        redis_coon = get_redis_connection('verify_codes')
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

        # 创建组织payload载荷的方法
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        # 创建生成jwt token数据的方法
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        # 传入用户对象 生成载荷数据
        payload = jwt_payload_handler(user)
        # 传入载荷 生成token数据
        token = jwt_encode_handler(payload)

        user.token = token
        user.save()

        return user
