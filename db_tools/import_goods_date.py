# -*- coding: utf-8 -*-
__author__ = 'oldlee'
__date__ = '2019-06-02 09:11'


import sys
import os

# 获取当前脚本文件的目录
pwd = os.path.dirname(os.path.realpath(__file__))
# 将当前文件的目录加入到os.path下面
sys.path.append(pwd+"../")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "MXshop.settings")

import django
django.setup()

from goods.models import Goods, GoodsCategory, GoodsImage

from db_tools.data.product_data import row_data

# 以下是导入商品信息
for goods_detail in row_data:
    goods = Goods()
    goods.name = goods_detail["name"]
    goods.market_price = float(int(goods_detail["market_price"].replace("￥", "").replace("元", "")))
    goods.shop_price = float(int(goods_detail["sale_price"].replace("￥", "").replace("元", "")))
    goods.goods_brief = goods_detail["desc"] if goods_detail["desc"] is not None else ""
    goods.goods_desc = goods_detail["goods_desc"] if goods_detail["goods_desc"] is not None else ""
    goods.goods_front_image = goods_detail["images"][0] if goods_detail["images"] else ""

    # 取goods_detail["categorys"]的倒数第一个字段，作为分类名称
    category_name = goods_detail["categorys"][-1]
    # 这里使用filter，不使用get的原因就在于，get获取不到数据就会报异常，而filter获取不到数据就返回空
    category = GoodsCategory.objects.filter(name=category_name)
    if category:
        goods.category = category[0]
    goods.save()

    for goods_image in goods_detail["images"]:
        # 实例化GoodsImage
        goods_image_instance = GoodsImage()
        goods_image_instance.image = goods_image
        goods_image_instance.goods = goods
        goods_image_instance.save()
