from django.core.files.storage import Storage
from django.conf import settings
# 上传文件需创建Fdfs_client对象并指明配置文件
from fdfs_client.client import Fdfs_client


class FastDFSStorage(Storage):
    def __init__(self, base_url=None, client_conf=None):
        """
        初始化
        :param base_url:用于构造图片完整路径使用 图片服务器的域名
        :param client_conf:FastDFS客户端配置文件的路径
        """
        if base_url is None:
            base_url = settings.FDFS_URL
        self.base_rul = base_url
        if client_conf is None:
            client_conf = settings.FDFS_CLIENT_CONF
        self.client_conf = client_conf

    def _save(self, name, content):
        """
        在FastDFS中保存文件
        name: 上传文件名称 1.jpg
        content: 包含上传文件内容的File对象，可以通过content.read()获取上传文件的内容
        """
        client = Fdfs_client(self.client_conf)

        # 上传文件
        res = client.upload_appender_by_buffer(content.read())
        if res.get('Status') != 'Upload successed.':
            raise Exception('上传文件到FDFS系统失败')

        # 获取文件id
        file_id = res.get('Remote file_id')
        return file_id

    def exists(self, name):
        """
        django框架在调用文件存储类中的_save进行文件保存之前，会先调用文件存储类中的exists方法
        判断文件名跟文件存储系统中已有的文件是否冲突
        name: 上传文件名称 1.jpg
        """
        return False

    def url(self, name):
        """
        获取可访问到文件的完整的url地址:
        name: 数据表中存储的文件id
        """
        return self.base_rul + name
