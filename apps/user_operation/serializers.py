# -*- coding: utf-8 -*-
__author__ = 'oldlee'
__date__ = '2020-02-06 21:36'

import re
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from .models import UserFav,UserLeavingMessage, UserAddress
from goods.serializers import GoodsSerializer
from MXshop.settings import REGEX_MOBILE


#这里再做一个序列化，并嵌套商品的序列化，返回商品信息
class UserFavDetailSerializer(serializers.ModelSerializer):
    goods =GoodsSerializer()
    class Meta:
        model = UserFav
        fields = ("goods","id")


class UserFavSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    class Meta:
        model = UserFav
        #这里使用vaidators的UniqueTogeterValidator对model里的对数据做唯一验证
        validators = [
            UniqueTogetherValidator(
                queryset=UserFav.objects.all(),
                fields=("user", "goods"),
                message = "已经收藏过了"
            )

        ]
        #在处理这种serializer的时候，如果会设计到删除功能，就最好在下面将id也返回回来
        fields = ("user","goods","id")


class LeavingMessageSerializer(serializers.ModelSerializer):
    #这里直接获取当前用户
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    # 这里要重写add_time，read_only=True作用为这个值，只返回不提交，和write_only是只提交不返回，而read_only是只返回不提交
    # 这里还有个问题，前端显示时间格式为：2020-02-09T15:37:44.652584，需要将add_time格式化，配置for
    add_time = serializers.DateTimeField(read_only=True, format="%Y-%m-%d %H:%M:%S")
    class Meta:
        model = UserLeavingMessage
        fields = ("user","message_type","subject","message","file","add_time","id")


class UserAddressSerializer(serializers.ModelSerializer):
    # 这里直接获取当前用户
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    # 这里要重写add_time，read_only=True作用为这个值，只返回不提交，和write_only是只提交不返回，而read_only是只返回不提交
    # 这里还有个问题，前端显示时间格式为：2020-02-09T15:37:44.652584，需要将add_time格式化，配置for
    add_time = serializers.DateTimeField(read_only=True, format="%Y-%m-%d %H:%M:%S")
    # 这里自定义一个validate对地址中多一些字段做验证，如手机号
    signer_mobile = serializers.CharField(max_length=11, min_length=11) #验证长度
    address = serializers.CharField(required=True, label="详细地址aa",help_text="详细地址a")


    #这里方法的名称，在validate的_后面一个要跟上与被验证字段一样的内容：signer_mobile
    def validate_signer_mobile(self,signer_mobile):
        #验证手机号的合法性
        if not re.match(REGEX_MOBILE, signer_mobile):
            raise serializers.ValidationError("手机号非法")
        return signer_mobile

    class Meta:
        model = UserAddress
        fields = ("user","province","city","district","address", "signer_name","signer_mobile", "add_time","id")

