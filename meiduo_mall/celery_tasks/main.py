from celery import Celery

# 创建Celery实例对象
celery_app = Celery('celery_tasks')

# 加载配置  根据配置文件位置
celery_app.config_from_object('celery_tasks.config')

# 自动寻找任务文件tasks.py
celery_app.autodiscover_tasks(['celery_tasks.sms'])