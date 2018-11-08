from django.conf import settings
from celery_tasks.main import celery_app
# 导入Django内置发送邮件函数
from django.core.mail import send_mail


@celery_app.task(name='send_verify_email')
def send_verify_email(email, verify_url):
    # 设置邮件内容
    html_message = '<p>尊敬的用户您好！</p>' \
                   '<p>感谢您使用美多商城。</p>' \
                   '<p>您的邮箱为：%s 。请点击此链接激活您的邮箱：</p>' \
                   '<p><a href="%s">%s<a></p>' % (email, verify_url, verify_url)
    # 调用django.core.mail种的send_mail方法进行邮件发送
    send_mail(subject='注册激活', message='', from_email=settings.EMAIL_FROM, recipient_list=[email],
              html_message=html_message)
