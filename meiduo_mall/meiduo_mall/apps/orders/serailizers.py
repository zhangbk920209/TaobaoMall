from decimal import Decimal

from django_redis import get_redis_connection
from rest_framework import serializers
from datetime import datetime
from goods.models import SKU
from orders.models import OrderInfo, OrderGoods


class OrderSKUSeriailizer(serializers.ModelSerializer):
    count = serializers.IntegerField(label='商品数量')

    class Meta:
        model = SKU
        fields = ('id', 'price', 'default_image_url', 'count', 'name')


class OrderSaveSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderInfo
        fields = ('order_id', 'address', 'pay_method')
        extra_kwargs = {
            'order_id': {
                'read_only': True
            },
            'address': {
                'write_only': True,
                'required': True
            },
            'pay_method': {
                'write_only': True,
                'required': True
            }
        }

    def create(self, validated_data):
        # 获取当前下单用户
        user = self.context['request'].user

        # 生成订单编号  日期+用户ID
        order_id = datetime.now().strftime('%Y%m%d%H%M%S') + '%010d' % user.id

        # 获取校验完成的参数
        address = validated_data['address']
        pay_method = validated_data['pay_method']

        total_count = 0
        total_amount = Decimal(10)
        freight = Decimal(10)

        # 根据用户选择支付方式选择订单状态
        if pay_method == OrderInfo.PAY_METHODS_ENUM['CASH']:
            status = OrderInfo.ORDER_STATUS_ENUM['UNSEND']
        else:
            status = OrderInfo.ORDER_STATUS_ENUM['UNPAID']

        # 使用三元表达式
        status = OrderInfo.ORDER_STATUS_ENUM['UNSEND'] if pay_method == OrderInfo.PAY_METHODS_ENUM['CASH'] else \
        OrderInfo.ORDER_STATUS_ENUM['UNPAID']

        # 实例订单对象
        order = OrderInfo.objects.create(
            order_id=order_id,
            user_id=user.id,
            address=address,
            pay_method=pay_method,
            total_count=total_count,
            total_amount=total_amount,
            freight=freight,
            status=status
        )

        # 获取并添加订单商品信息
        redis_conn = get_redis_connection('cart')

        cart_key = 'cart_%s' % user.id
        cart_selected_key = 'cart_selected_%s' % user.id

        cart_dict = redis_conn.hgetall(cart_key)
        skus_ids = redis_conn.smembers(cart_selected_key)

        for sku_id in skus_ids:

            count = int(cart_dict[sku_id])

            sku = SKU.objects.get(id=sku_id)

            sku.stock -= count
            sku.sales += count
            sku.save()

            OrderGoods.objects.create(
                sku=sku,
                price=sku.price,
                order_id=order_id,
                count=count,
            )

            total_count += count
            total_amount += sku.price*count


        order.total_amount += freight
        order.total_count += total_count
        order.total_amount += total_amount

        order.save()

        pl = redis_conn.pipeline()
        pl.srem(cart_selected_key, skus_ids)
        pl.hdel(cart_dict, skus_ids)
        pl.execute()

        return order_id