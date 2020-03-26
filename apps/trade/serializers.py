# -*- coding: utf-8 -*-
__author__ = 'oldlee'
__date__ = '2020-02-10 11:48'
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
import time

from .models import ShoppingCart,OrderInfo,OrderGoods
from goods.models import Goods
from goods.serializers import GoodsSerializer
from utils.alipayapi import AliPay
from MXshop.settings import private_key_path,ali_pub_key_path


class ShopcartDetailSerializer(serializers.ModelSerializer):
    goods = GoodsSerializer(many=False)
    class Meta:
        model = ShoppingCart
        fields = "__all__"


# 这里要继承serializer，因为如果是继承ModelSerializer的话，就会一直验证唯一合集的user，goods，验证失败
class ShoppingCartSerializer(serializers.Serializer):
    user = serializers.HiddenField(
        default= serializers.CurrentUserDefault()
    )
    nums = serializers.IntegerField(required=True, min_value=1,
                                    error_messages={
                                        "required":"请选择商品数量",
                                        "min_value":"商品数量不能小于1"
                                    })
    # 这里goods，由于这里的serializer是继承serializer，所以要指明queryset,从Goods里取
    goods = serializers.PrimaryKeyRelatedField(required=True, queryset=Goods.objects.all())

    #然后就对serializer的creater方法只有重写
    # 这里用户post过来的user就保存在self中，而前面序列化的nums和goods就在validated_data中
    def create(self, validated_data):
        # 如果是view，那么user就在self.request里，如果是serializer，那么当前用户user就在self.context["request"]里，即self的上下文里
        user = self.context["request"].user
        nums = validated_data["nums"]
        goods = validated_data["goods"]

        #然后根据这些信息，在数据库查询，看是否能查到数据
        existed = ShoppingCart.objects.filter(user=user, goods=goods)

        if existed:
            #如果存在，那就拿到最新数据记录，并且把新的nums加进去就可以了
            existed = existed[0]
            existed.nums += nums
            existed.save()
        else:
            #如果不存在，就进行保存，并且把前面validated_data传进去
            existed = ShoppingCart.objects.create(**validated_data)
        return existed

    # 这里还有个问题，就是由于调用的serializer而不是Modelserializer，所以在做数据更新的时候，即调用八色、serializer的update方法时，会报错
    #因为Modelserializer里的对update已经重写了，所以这里我们继承serializer也要重写
    def update(self, instance, validated_data):
        instance.nums = validated_data["nums"]
        instance.save()
        return instance


class OrderGoodsSerializer(serializers.ModelSerializer):
    # 这个字段可不唯一，所以many=False
    goods = GoodsSerializer(many=False)

    class Meta:
        model = OrderGoods
        fields = "__all__"


class OrderDetailSerializer(serializers.ModelSerializer):
    # 保证这个字段唯一
    goods = OrderGoodsSerializer(many=True)
    alipay_url = serializers.SerializerMethodField(read_only=True)

    # 方法名称由get链接字段名称，就可以自动去找对应的字段
    # 这里我们传入obj，也就是当前serializer的model
    def get_alipay_url(self, obj):
        alipay = AliPay(
            appid="2021001129619051",
            app_notify_url="http://47.101.69.87:8000/alipay/return/",
            app_private_key_path=private_key_path,
            alipay_public_key_path=ali_pub_key_path,  # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            debug=False,  # 默认False,
            return_url="http://47.101.69.87:8000/alipay/return/"
        )
        url = alipay.direct_pay(
            # 将当前model的值赋值给url
            subject=obj.order_sn,
            out_trade_no=obj.order_sn,
            total_amount=obj.order_mount
        )
        re_url = "https://openapi.alipay.com/gateway.do?{data}".format(data=url)
        # 生成链接并返回
        return re_url

    class Meta:
        model=OrderInfo
        fields = "__all__"


class OrderSerializer(serializers.ModelSerializer):
    #接口数据里隐藏用户列表
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    #定义以下字段，只读（read_only），不可写，也就是只能后台生成和修改
    pay_status = serializers.CharField(read_only=True)
    trade_no = serializers.CharField(read_only=True)
    order_sn = serializers.CharField(read_only=True)
    pay_time = serializers.DateTimeField(read_only=True)
    add_time = serializers.DateTimeField(read_only=True, format="%Y-%m-%d %H:%M:%S")
    # 添加支付宝支付链接的serializer，也是只读，由系统生成
    alipay_url = serializers.SerializerMethodField(read_only=True)

    # 方法名称由get链接字段名称，就可以自动去找对应的字段
    # 这里我们传入obj，也就是当前serializer的model
    def get_alipay_url(self,obj):
        alipay = AliPay(
            appid="2021001129619051",
            app_notify_url="http://47.101.69.87:8000/alipay/return/",
            app_private_key_path=private_key_path,
            alipay_public_key_path=ali_pub_key_path,  # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            debug=False,  # 默认False,
            return_url="http://47.101.69.87:8000/alipay/return/"
        )
        url = alipay.direct_pay(
            # 将当前model的值赋值给url
            subject=obj.order_sn,
            out_trade_no=obj.order_sn,
            total_amount=obj.order_mount
        )
        re_url = "https://openapi.alipay.com/gateway.do?{data}".format(data=url)
        # 生成链接并返回
        return re_url

    #这里计算一个订单号，根据随机号，当前时间，当前用户的id，然后返回算出的订单号
    def generate_order_sn(self):
        from random import Random
        random_ins = Random()
        order_sn = "{time_str}{userid}{ranstr}".format(time_str=time.strftime("%Y%m%d%H%M%S"),
                                                       userid=self.context["request"].user.id,
                                                       ranstr=random_ins.randint(10,99))
        return order_sn

#调用全局的验证函数，取出model的order_sn，将上面算出的order_sn赋值给他
    def validate(self, attrs):
        attrs["order_sn"]=self.generate_order_sn()
        return attrs

    class Meta:
        model = OrderInfo
        # fields = ("user","order_sn","trade_no","pay_status","post_script","order_mount","pay_time","address","signer_name","singer_mobile","add_time")
        fields = "__all__"