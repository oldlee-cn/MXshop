from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.authentication import SessionAuthentication

from .models import UserFav, UserLeavingMessage, UserAddress
from utils.permissions import IsOwnerOrReadOnly
from .serializers import UserFavSerializer, UserFavDetailSerializer, LeavingMessageSerializer, UserAddressSerializer


class UserFavset(mixins.CreateModelMixin, mixins.ListModelMixin, mixins.DestroyModelMixin, mixins.RetrieveModelMixin,viewsets.GenericViewSet):
    """
    list:
        用户获取收藏列表
    create：
        用户添加收藏
    delete：
        用户取消收藏
    """
    #添加用户权限，也就是用户只能查看、操作自己的收藏列表
    # 这里要使用到permissions，他是用于权限验证，而Auth是用于用户验证的
    #这里我们就要用到permissions里面from rest_framework.permissions import IsAuthenticated，来判断用户是否登录
    #这样，如果用户在未登录的情况下，访问mixins.ListModelMixin，然后IsAuthenticated就会抛401异常
    # 除以上之外，还需要验证当前操作的用户的是不是request过来的用户，就需要我们重写IsOwnerOrReadOnly，即from utils.permissions import IsOwnerOrReadOnly
    permission_classes = (IsAuthenticated,IsOwnerOrReadOnly)

    serializer_class = UserFavSerializer
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    lookup_field = "goods"

    # 这里就不能获取全部用户了，只能获取当前用户，也就是request提交过来的user
    # queryset = UserFav.objects.all()
    def get_queryset(self):
        return UserFav.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        instance = serializer.save()
        goods = instance.goods
        goods.fav_num += 1
        goods.save()

    # 按照情况配置serializer
    def get_serializer_class(self):
        if self.action == "list":
            return UserFavDetailSerializer
        elif self.action == "create":
            return UserFavSerializer


class LeavinngMessageViewset(mixins.ListModelMixin, mixins.CreateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    """
    list:
        留言列表
    create:
        创建留言
    delete:
        删除留言
    """
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    serializer_class = LeavingMessageSerializer

    # 这里就不能获取全部用户了，只能获取当前用户，也就是request提交过来的user
    # queryset = UserFav.objects.all()
    def get_queryset(self):
        return UserLeavingMessage.objects.filter(user=self.request.user)


#如果要继承：mixins.ListModelMixin, mixins.CreateModelMixin, mixins.DestroyModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet
# 等所有的mixins和viewset，那么只需要继承一个viewsets.ModelViewSet
class UserAddressviewset(viewsets.ModelViewSet):
    """
    收货地址管理
    list:
        所有地址
    create:
        增加地址
    update:
        更新数据
    delete:
        删除地址
    """
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    serializer_class = UserAddressSerializer

    def get_queryset(self):
        return UserAddress.objects.filter(user = self.request.user)
