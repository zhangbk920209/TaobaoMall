from rest_framework import serializers

from goods.models import SKU
from drf_haystack.serializers import HaystackSerializer
from goods.search_indexes import SKUIndex


# 用户浏览记录商品序列化器类
class SKUSerializer(serializers.ModelSerializer):
    class Meta:
        model = SKU
        fields = ('id', 'name', 'price', 'comments', 'default_image_url')


# 搜索引擎序列化器类
class SKUIndexSerializer(HaystackSerializer):
    object = SKUSerializer(read_only=True)

    class Meta:
        # 指定对应索引类
        index_classes = [SKUIndex]
        # 指定序列化字段
        fields = ('text', 'object')
