import os
from celery import Celery

# 因设计使用django内置模块， 故检查系统环境变量 设置配置模块
if not os.environ.get('DJANGO_SETTINGS_MODULE'):
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "meiduo_mall.settings.dev")

# 创建Celery实例对象
celery_app = Celery('celery_tasks')

# 加载配置  根据配置文件位置
celery_app.config_from_object('celery_tasks.config')

# 自动寻找任务文件tasks.py
celery_app.autodiscover_tasks(['celery_tasks.sms', 'celery_tasks.email', 'celery_tasks.html'])
