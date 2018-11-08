import logging
from celery_tasks.main import celery_app
from celery_tasks.sms.yuntongxun.sms import CCP

# 设置模板ID
TEMPLATE_ID = 1

# 创建日志器
logger = logging.getLogger('django')


# 创建任务函数
@celery_app.task(name='send_sms_codes')
def send_sms_codes(mobile, sms_code, expire):
    try:
        result = CCP().send_template_sms(mobile, [sms_code, expire], TEMPLATE_ID)
    except Exception as e:
        logger.error("发送验证码短信[异常][ mobile: %s, message: %s ]" % (mobile, e))

    else:
        if result != 0:
            logger.warning("发送短信验证码[失败][ mobile: %s ]" % mobile)
        else:
            logger.info("发送短信验证码[正常][ mobile: %s ]" % mobile)
