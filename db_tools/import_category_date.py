# -*- coding: utf-8 -*-
__author__ = 'oldlee'
__date__ = '2019-06-02 07:29'

# 独立使用django的model

import sys
import os

pwd = os.path.dirname(os.path.realpath(__file__))
sys.path.append(pwd+"../")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "MXshop.settings")

import django
django.setup()

from goods.models import GoodsCategory

from db_tools.data.category_data import row_data

# 以下是导入商品分类的信息
for lev1_cat in row_data:
    # 实例化GoodsCategory
    lev1_intance = GoodsCategory()
    lev1_intance.code = lev1_cat["code"]
    lev1_intance.name = lev1_cat["name"]
    # lev1_intance的分类类型是1
    lev1_intance.category_type = '1'
    lev1_intance.save()

    for lev2_cat in lev1_cat["sub_categorys"]:
        # 实例化GoodsCategory
        lev2_intance = GoodsCategory()
        lev2_intance.code = lev2_cat["code"]
        lev2_intance.name = lev2_cat["name"]
        # lev2_intance的分类类型是2
        lev2_intance.category_type = '2'
        # 指明lev2_intance的父类
        lev2_intance.parent_category = lev1_intance
        lev2_intance.save()

        for lev3_cat in lev2_cat["sub_categorys"]:
            lev3_intance = GoodsCategory()
            lev3_intance.code = lev3_cat["code"]
            lev3_intance.name = lev3_cat["name"]
            lev3_intance.category_type = '3'
            lev3_intance.parent_category = lev2_intance
            lev3_intance.save()
