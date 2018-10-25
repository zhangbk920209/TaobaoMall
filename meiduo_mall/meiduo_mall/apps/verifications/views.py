import random,logging
from django_redis import get_redis_connection
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

# from meiduo_mall.meiduo_mall.libs.yuntongxun.sms import CCP
# 如果未设置app为资源路径 则导入constants如下
# from meiduo_mall.meiduo_mall.apps.verifications import constants
# 设置app为资源路径后如下
from verifications import constants

# 如果为设置meiduo_mall为资源路径 导入CCP如下
# from meiduo_mall.meiduo_mall.libs.yuntongxun.sms import CCP
# 设置meiduo_mall为资源路径后如下
from meiduo_mall.libs.yuntongxun.sms import CCP


logger = logging.getLogger('django')


# GET /sms_code/(?P<mobile>1[3-9]\d{9})/
class SMSCodeView(APIView):
    def get(self, request, mobile):
        """
        获取短信验证码：
        1、随机生成六位手机验证码
        2、使用云通讯给'mobile'发送短信
        3、在redis种保存短信验证码内容 'mobile':'验证码'
        4、返回响应
        :return:
        """
        # 构造短信验证码
        sms_code = "%06d" % random.randint(1, 999999)
        print(sms_code)
        # 使用云通讯给'mobile'发送短信
        redis_coon = get_redis_connection('verify_codes')
        redis_coon.setex('sms_%s' % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
        # 在redis种保存短信验证码内容 'mobile':'验证码'
        try:
            result = CCP().send_template_sms(mobile, [sms_code, constants.SMS_CODE_REDIS_EXPIRES//60], constants.SMS_CODE_TEMP_ID)
        except Exception as e:
            logger.error(e)
            return Response({'message': '发送短信异常'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        if result != 0:
            return Response({'message': '发送短信失败'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        # 返回响应
        return Response({'message': '发送短信成功'})

