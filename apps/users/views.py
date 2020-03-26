from django.shortcuts import render

# Create your views here.

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from .models import VerifyCode
from django.db.models import Q
from rest_framework.mixins import CreateModelMixin
from rest_framework import mixins
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from random import choice
from rest_framework_jwt.serializers import jwt_encode_handler,jwt_payload_handler
from rest_framework import permissions
from rest_framework import authentication
from rest_framework_jwt.authentication import JSONWebTokenAuthentication


from .serializers import SmsSerializer, UserRegSerializer, UserDetailSerializer
from utils.alisms import Alisms
from MXshop.settings import API_KEY

User = get_user_model()


class Custombackend(ModelBackend):
    """
    自定义用户验证，比如用户名使用手机号
    """
    def authenticate(self, username=None, password=None, **kwargs):
        try:
            # 如果用户名是手机或者用户名，这个字段是根据数据库字段里来的
            # 都获取过来，赋值给user
            user=User.objects.get(Q(username=username)|Q(moblie=username))
            # 这里再把用户登录输入的密码获取出来，进行加密，然后再和数据库的以加密密码做比对，如果相等，就返回该用户名
            if(user.check_password(password)):
                return user
        except Exception as e:
            return None

# 以上完成后，将此认证模式配置大setting.py的AUTHENTICATION_BACKENDS函数中去


#这里我们单独建一个类对发送验证码
class SmsCodeViewset(CreateModelMixin, viewsets.GenericViewSet):
    """
    发送验证码
    """

    #首先配置对手机号验证的serializer
    serializer_class = SmsSerializer


    #生成一个四位数的验证码，需要导入from random import choices
    def generate_code(self):
        seeds = '1234567890'    #定义种子
        random_str = []
        for i in range(4):
            random_str.append(choice(seeds))
        return "".join(random_str)


    #然后重写CreateModelMixin的create，需要先导入Response和status
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        #下面的is_valid的作用是，如果调用失败，这里直接报异常，就不会再往下走，
        #而且raise_exceotion=True的作用是，如果is_valid抛了异常，这里就会给我们的drf返回400状态，便于前端处理
        serializer.is_valid(raise_exception=True)

        #先从serializer里取出我们已经验证好的mobile
        # serializer验证通过的结果都会保存在validates_data这个里面
        moblie = serializer.validated_data['moblie']

        #引入验证码发送api
        yunpian = Alisms(API_KEY)
        #传入参数：随机验证码和手机号,并返回一个code
        code = self.generate_code()
        sms_status = yunpian.send_sms(code=code, moblie=moblie)

        #云片网短信发送成功返回0，其他code代表发送失败

        #然后就是解析返回的code给用户或者前端做一个提醒
        # 如果不等于0，即失败,返回400状态码
        if sms_status['code'] != 0:
            return Response({
                'moblie':sms_status["msg"]
            },status=status.HTTP_400_BAD_REQUEST)
        #否则返回手机号和201状态码,即完成创建，需要现将验证码保存进数据库，需要现引入from .models import VerifyCode
        else:
            code_record = VerifyCode(code=code, moblie=moblie)
            code_record.save()
            return Response({
                "moblie":moblie
            }, status = status.HTTP_201_CREATED)


#继承mixins.RetrieveModelMixin，便于读单条数据
class UserViewset(CreateModelMixin, mixins.UpdateModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    # 配置srializers
    serializer_class = UserRegSerializer
    # 这个queryset不要忘记
    queryset = User.objects.all()
    authentication_classes = (JSONWebTokenAuthentication, authentication.SessionAuthentication)

    #这里动态serializer
    def get_serializer_class(self):
        if self.action == "retrieve":   #如果是读数据
            return UserDetailSerializer
        elif self.action == "create":   #如果是创建数据
            return UserRegSerializer
        return UserDetailSerializer

    #这里动态获取验证，也就是用户注册时不验证登录，读数据时才验证，这里的self.action,只有继承viewsets，才可以用
    def get_permissions(self):
        if self.action == "retrieve":   #如果是读数据
            return [permissions.IsAuthenticated()]
        elif self.action == "create":   #如果是创建数据
            return []
        return []


    # 这里如果需要用户在前端注册后直接完成登录，这里就需要重写CreateModelMixin的create方法
    # 获取到user，然后根据user生成JWT的token

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)


        # 这里就可以根据下面对 perform_create 的重写，返回serializer的model对象，取到user
        user = self.perform_create(serializer)
        # 前端的toke，在serializer.data里面，我们生成JWT的token后给他赋值
        re_dict = serializer.data
        # 如果要根据user生成JWT的token就需要导入:
        # from rest_framework_jwt.serializers import jwt_encode_handler, jwt_payload_handler
        # 这两个函数
        payload = jwt_payload_handler(user) #根据user生成payload
        re_dict['token'] = jwt_encode_handler(payload) #然后根据payload生成token，这里注意token的写法和前端保持一致
        #除了返回token、还要返回user
        re_dict["user"] = user.name if user.name else user.username #如果是name就返回，如果是username就返回username



        headers = self.get_success_headers(serializer.data)
        # 然后这里返回的时候，就不返回serializer.data了，就返回处理过的re_dict
        return Response(re_dict, status=status.HTTP_201_CREATED, headers=headers)

    #这里返回当前用户
    def get_object(self):
        return self.request.user

        # 这个函数也要重载，因为原先CreateModelMixin里面的perform_create函数只是调用保存，没有返回
    def perform_create(self, serializer):
        return serializer.save()



















