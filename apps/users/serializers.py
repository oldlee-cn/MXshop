# -*- coding: utf-8 -*-
__author__ = 'oldlee'
__date__ = '2020-02-02 10:07'
import re
from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.validators import UniqueValidator

from MXshop.settings import REGEX_MOBILE
from datetime import datetime
from datetime import timedelta
from .models import VerifyCode


User = get_user_model()


#这里使用了Serializer，而不是ModelSerializer，因为这里对用户登录进行验证，我们的user里的验证码表的code是必填项，这里如果还是必填项，那么验证肯定不能通过
#因为这里的验证只对手机号进行验证
class SmsSerializer(serializers.Serializer):
    #首先验证手机长度为11位
    moblie = serializers.CharField(max_length=11)
    #然后进行其他验证

    def validate_moblie(self, moblie):
        """
        验证手机号
        :param mobile:
        :return:
        """

        #首先验证手机是否已经被注册，首先要查询数据库用户表，需要因引入
        # from django.contrib.auth import get_user_model
        # User = get_user_model()
        if User.objects.filter(moblie=moblie).count():      #如果查询该手机号结果存在
            raise serializers.ValidationError("用户已经存在") #返回错误"手机号已存在"

        #验证手机号码是否合法，这需要使用正则表达式，科技将正则表达式注册在项目的setting.py里
        #需要先引入re模块和setting.py里的正则表达式
        if not re.match(REGEX_MOBILE,moblie):   #如果验证不通过
            raise serializers.ValidationError("手机号非法")


        # 验证手机验证码发送的频率
        one_mintes = datetime.now()- timedelta(hours=0,minutes=1, seconds=0) #取出1分钟之前的时间
        #__gt=是大于的意思，这里如果添加数据库记录的时间大于一分钟之前的时间，说明距离上次验证码发送还未超过一分钟
        if VerifyCode.objects.filter(add_time__gt=one_mintes):#这里需要拿到数据库的该条记录的添加时间跟一分钟之前的时间做对比，需要引入from .models import VerifyCode
            raise serializers.ValidationError("距离上次发送未超过60s")

        #最后返回 手机号
        return moblie


class UserDetailSerializer(serializers.ModelSerializer):
    """
    获取用户详情序列化
    """
    class Meta:
        model = User
        fields = ("name","moblie","email","birthday","gender")


class UserRegSerializer(serializers.ModelSerializer):
    """
    用户注册的serializer
    """
    #这里设置write_only为true之后，该字段就不会被验证数据，就不会报错，从而只调用该字段的serializer程序，不再返回该字段值
    code = serializers.CharField(required=True, max_length=4, min_length=4,label="验证码",write_only=True,
                                 #可以自定义一些错误提示，其中blank是针对必填为空时的自定义提示
                                 error_messages={
                                     "blank":"请输入验证码1",
                                     "required":'请输入验证码',
                                     "max_length":"格式错误",
                                     "min_length":"格式错误"
                                 },
                                 help_text="验证码")
    #使用validate来验证字段，更简便，需要先导入from rest_framework.validators import UniqueValidator
    #然后就可以自定义报错信息
    username = serializers.CharField(required=True,allow_blank=False,label="用户名",help_text="用户名",
                                 validators=[UniqueValidator(User.objects.all(), message="用户名已经春在")]
                                 )
    # 这里的password的write_only设置为True也是一样，值调用serializers的验证程序，不返回数据
    password = serializers.CharField(write_only=True,
        style={"input_type":"password"}
    )
# -------------以下这一段也可以用signals文件的逻辑来代替，以此保持serializers文件的代码优雅
    # 这里modelserializer有个私有方法create，取到user，然后model有继承AbstractUser，里面也有个set_password直接加密保存方法
    # def create(self, validated_data):
    #     user = super(UserRegSerializer,self).create(validated_data=validated_data)
    #     user.set_password(validated_data["password"])
    #     user.save()
    #     return user #最后返回user

# -------------以上这一段也可以用signals文件的逻辑来代替，以此保持serializers文件的代码优雅
    def validate_code(self, code):
        """
        验证code字段。首先是频率，然后是是否相等，最后我们也可以return，也可以不返回，因我们最主要是做验证
        :param code:
        :return:
        """
        # 这里用到了initial_data，这个是用户在前端post过来的数据都会放在initial_data里面了，所以我们这里可以获取到手机号，根据手机号拿到code
        # 这里用户前端post的就是用户名，即手机号，我们需要利用添加时间来排序，取出最新的
        verify_records = VerifyCode.objects.filter(moblie=self.initial_data["username"]).order_by("-add_time")
        # 如果拿到了记录，我们就拿到最新一条记录
        if verify_records:
            last_records = verify_records[0]
            five_mintes = datetime.now()-timedelta(hours=0, minutes=5, seconds=0)
            if last_records.add_time < five_mintes:
                raise serializers.ValidationError("验证码过期")
            #再如果last_records不等于本方法传递进来的code，那就是验证码错误
            if str(last_records) != code:
                raise  serializers.ValidationError("验证码错误")
        else:
            raise serializers.ValidationError("验证码错误/不存在")

    def validate(self, attrs):
        attrs['moblie'] = attrs['username']
        del attrs['code']
        return attrs

    class Meta:
        model = User
        fields = ("username","code",'moblie',"password")

