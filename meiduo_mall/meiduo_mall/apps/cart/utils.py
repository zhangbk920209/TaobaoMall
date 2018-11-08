import pickle
import base64

from django_redis import get_redis_connection


# 合并购物车函数
def merge_cart_cookie_to_redis(request, response, user):
    cart_cookie = request.COOKIES.get('cart')
    if not cart_cookie:
        return

    cart_dict = pickle.loads(base64.b64decode(cart_cookie))

    if not cart_dict:
        return

    cart = {}

    cart_sku_redis_add = []

    cart_sku_redis_rem = []

    for sku_id, sku_dict in cart_dict.items():
        cart[sku_id] = sku_dict['count']
        if sku_dict['selected']:
            cart_sku_redis_add.append(sku_id)
        else:
            cart_sku_redis_rem.append(sku_id)

    redis_conn = get_redis_connection('cart')
    cart_key = 'cart_%s' % user.id
    cart_selected_key = 'cart_selected_%s' % user.id

    pl = redis_conn.pipeline()

    pl.hmset(cart_key, cart)

    if cart_sku_redis_add:
        pl.sadd(cart_selected_key, *cart_sku_redis_add)

    if cart_sku_redis_rem:
        pl.srem(cart_sku_redis_rem, *cart_sku_redis_rem)

    pl.execute()

    response.delete_cookie('cart')




