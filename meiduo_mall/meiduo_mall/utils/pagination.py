from rest_framework.pagination import PageNumberPagination


# 自定义分页类
class StandarResultPagination(PageNumberPagination):
    # 分页页容量
    page_size = 6
    # 前端发送的每页数目关键字名，默认为None
    page_size_query_param = 'page_size'
    # 前端最多能设置的每页数量
    max_page_size = 20
