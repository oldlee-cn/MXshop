# -*- coding: utf-8 -*-
__author__ = 'oldlee'
__date__ = '2020-01-14 22:24'

import django_filters
from django.db.models import Q
from .models import Goods

class GoodsFilter(django_filters.rest_framework.FilterSet):
    # 这里注意，在自从 django-filter2.0之后 将Filter的name字段 更名为 field_name 所以需要这样写，否则会报错name错误
    pricemin = django_filters.NumberFilter(field_name="shop_price",lookup_expr="gte",help_text="最小值")
    pricemax = django_filters.NumberFilter(field_name="shop_price",lookup_expr="lte")
    # 这里忽略大小写，就在contains前面加上i，即icontainns
    # name = django_filters.CharFilter(name="name",lookup_expr="contains")

    # 把下面的方法注册近过滤项
    top_category = django_filters.NumberFilter(method="top_category_filter")

    # 获取某一分类下的所有商品，含此分类是商品的所属分类，所属父分类，所属父父分类，其中value是商品分类id，name是商品分类
    def top_category_filter(self, queryset, name, value):
        # 返回该分类下所有相关的产品信息
        return queryset.filter(Q(category_id=value)|Q(category__parent_category_id=value)|Q(category__parent_category__parent_category_id=value))

    class Meta:
        model = Goods
        fields = ['pricemin','pricemax', "is_hot","is_new"]
