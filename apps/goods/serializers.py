# -*- coding: utf-8 -*-
__author__ = 'oldlee'
__date__ = '2019-06-14 08:44'

from rest_framework import serializers
from django.db.models import Q


from goods.models import Goods, GoodsCategory, GoodsImage, HotSearchWords,Banner,GoodsCategorybrand,IndexAd

# class GoodsSerializer(serializers.Serializer):
#     name = serializers.CharField(required=True)
#     click_num = serializers.IntegerField(default=0)
#     goods_front_image = serializers.ImageField()
#     add_time = serializers.DateTimeField()
#     def create(self, validated_data):
#         """
#         返回一个models的实例
#         :param validated_data:
#         :return:
#         """
#         return Goods.objects.create(**validated_data)


class CategorySerializer3(serializers.ModelSerializer):
    class Meta:
        model = GoodsCategory()
        fields = '__all__'


class CategorySerializer2(serializers.ModelSerializer):
    sub_cat = CategorySerializer3(many=True)

    class Meta:
        model = GoodsCategory
        fields = '__all__'


#序列化商品分类的model
# 首先只展示一级大类，sub_cat = CategorySerializer2(many=True)的作用，就是把一级大类下面的二级类放进来了
# 而CategorySerializer2里面的sub_cat = CategorySerializer3(many=True)也是同理
class CategroySerializer(serializers.ModelSerializer):
    sub_cat = CategorySerializer2(many=True)
    class Meta:
        model = GoodsCategory
        fields = '__all__'

class GoodsImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodsImage
        fields = ("image",)

    # 类似与Django的Modelform，更简单的管理model的数据
class GoodsSerializer(serializers.ModelSerializer):
    # 如果要列出商品中商品分类这个外键的具体属性，这里就要先对商品分类属性的serializer进行一下实例化
    # 这的赋值字段要保证与Goods的model里的外键字段名一致
    category = CategroySerializer()
    images = GoodsImageSerializer(many=True)
    class Meta:
        # 指明model
        model = Goods
        # 定义需要序列化的model字段
        # fields = ('name', 'click_num', 'market_price', 'add_time')
        # 序列化所有的字段
        fields = '__all__'


class HotWordsSerializer(serializers.ModelSerializer):
    class Meta:
        model = HotSearchWords
        fields = '__all__'


class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = "__all__"

# -----------------------下面对首页的商品分类展示楼层做数据展示：这里面是一对多的分类关系和商品信息，还包含一个广告图 -----------------------

# 先对品牌做serializer，好让下面的serializer嵌套
class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodsCategorybrand
        fields = "__all__"


class IndexCategorySerializer(serializers.ModelSerializer):
    # 嵌套品牌内容，brand有个外键指向category，而且一个brand有多个category，所以这里要用many=True，如果只一对一就many=false
    brands = BrandSerializer(many=True)
    #然后嵌套商品内容，这里就不能像上面的brand一样，反向获取serializer，因为，如果通过goods的category外键反向取的是第三级分类，我们这里需要第一级分类，
    #所以就需要我们像trade里面一样使用SerializerMethodField自己获取
    goods = serializers.SerializerMethodField()
    #获取2级分类
    sub_cat = CategorySerializer2(many=True)

    def get_goods(self,obj):
        #然后按照传进来的category的id，取出所有的商品数据
        all_goods = Goods.objects.filter(Q(category_id=obj.id)|Q(category__parent_category_id=obj.id)|Q(category__parent_category__parent_category_id=obj.id))
        #然后再对取到的商品数据序列化,然后指明many=True
        # 这里在对SerializerMethodField的字段做序列化的时候，是没有自动加上域名，生成完整图片链接的，所以要加上 context={"request":self.context['request']}
        goods_serializer = GoodsSerializer(all_goods,many=True, context={"request":self.context['request']})
        #最终他会将数据保存在。data里，返回即可
        return goods_serializer.data

    #对首页的分类广告序列化
    # 所以就需要我们像trade里面一样使用SerializerMethodField自己获取
    ad_goods = serializers.SerializerMethodField()

    def get_ad_goods(self,obj):
        goods_json = {}
        ad_goods = IndexAd.objects.filter(category_id=obj.id)
        if ad_goods:
            goods_ins = ad_goods[0].goods
            #这里返回的是serializer的实例，所以要返回。data才是真正的json数据
            # 这里在对SerializerMethodField的字段做序列化的时候，是没有自动加上域名，生成完整图片链接的，所以要加上 context={"request":self.context['request']}
            goods_json = GoodsSerializer(goods_ins,many=False, context={"request":self.context['request']}).data
        return goods_json
    class Meta:
        model = GoodsCategory
        fields = "__all__"