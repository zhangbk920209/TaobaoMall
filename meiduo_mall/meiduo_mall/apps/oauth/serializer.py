import base64
import os

from django_redis import get_redis_connection
from rest_framework import serializers

from oauth.models import OAuthQQUser
from oauth.utils import OAuthQQ
from users.models import User


class OAuthQQUserSerializer(serializers.ModelSerializer):
    mobile = serializers.RegexField(label='手机号', regex=r'1[3-9]\d{9}$', )
    sms_code = serializers.CharField(label='短信验证码', write_only=True)
    secret_openid = serializers.CharField(label='加密OpenID', write_only=True)
    token = serializers.CharField(label='JWTToken', read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'mobile', 'password', 'sms_code', 'secret_openid', 'token')
        extra_kwargs = {
            'password': {
                'max_length': 20,
                'min_length': 8,
                'write_only': True,
                'error_messages': {
                    'min_length': '仅允许8-20个字符的密码',
                    'max_length': '仅允许8-20个字符的密码',
                }
            },
            'username': {
                'read_only': True
            }
        }

    def validate(self, attrs):
        # 手机号格式已在字段定义过程进行验证
        # 短信验证码
        sms_code = attrs['sms_code']
        mobile = attrs['mobile']
        redis_coon = get_redis_connection('verify_codes')
        real_sms_code = redis_coon.get('sms_%s' % mobile)
        # 判断验证码是否过期
        if not real_sms_code:
            raise serializers.ValidationError('短信验证码已过期')
        # 判断验证码是否正确
        if sms_code != real_sms_code.decode():
            raise serializers.ValidationError('短信验证码错误')

        scret_openid = attrs['secret_openid']
        # 对加密后的open_id 即access_token进行校验
        openid = OAuthQQ.check_save_user_token(scret_openid)
        if not openid:
            raise serializers.ValidationError('Openid已失效')
        attrs['openid'] = openid
        # 如果用户存在，检查用户密码'
        try:
            user = User.objects.get(mobile=mobile)
        except User.DoesNotExist:
            user = None
        else:
            password = attrs['password']
            if not user.check_password(password):
                raise serializers.ValidationError('用户名密码错误')

        attrs['user'] = user
        return attrs

    def create(self, validated_data):
        user = validated_data['user']

        if not user:
            username = base64.b64encode(os.urandom(9)).decode()
            mobile = validated_data['mobile']
            password = validated_data['password']
            user = User.objects.create_user(mobile=mobile, password=password, username=username)

        # 获取类视图的对象，给类视图对象增加属性user，用来保存绑定用户对象
        # 以便在类视图中可以直接通过`self.user`获取绑定用户对象
        self.context['view'].user = user

        openid = validated_data['openid']
        OAuthQQUser.objects.create(openid=openid, user=user)

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
