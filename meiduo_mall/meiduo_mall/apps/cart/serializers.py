from rest_framework import serializers
from goods.models import SKU


# 购物车添加记录序列化器类
class CartSerializer(serializers.Serializer):
    sku_id = serializers.IntegerField(label='商品SKU编号', min_value=1)
    count = serializers.IntegerField(label='商品数量', min_value=1)
    selected = serializers.BooleanField(label='勾选状态', default=True)

    def validate(self, attrs):
        # 商品是否存在
        sku_id = attrs['sku_id']
        try:
            sku = SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            raise serializers.ValidationError('商品不存在')

        # 商品库存是否足够
        count = attrs['count']
        if count > sku.stock:
            raise serializers.ValidationError('库存不足')
        return attrs


# 购物车数据展示序列化器
class CartSKUSerializer(serializers.ModelSerializer):
    count = serializers.IntegerField(label='商品数量')
    selected = serializers.BooleanField(label='商品勾选状态', default=True)

    class Meta:
        model = SKU
        fields = ('id', 'name', 'default_image_url', 'price', 'count', 'selected')


# 购物车数据删除序列化器
class CartDeleteSerializer(serializers.Serializer):
    sku_id = serializers.IntegerField(label='商品SKU编号', min_value=1)

    def validate_sku_id(self, value):
        # 校验产品是否存在
        try:
            sku = SKU.objects.get(id=value)
        except SKU.DoesNotExist:
            raise serializers.ValidationError('产品不存在')

        return value


# 购物车勾选状态序列化器
class CartSelectionSerializer(serializers.Serializer):
    selected = serializers.BooleanField(label='购物车勾选状态')