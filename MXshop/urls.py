"""MXshop URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import url,include
import xadmin
from MXshop.settings import MEDIA_ROOT
from django.views.static import serve
from rest_framework.documentation import include_docs_urls
from rest_framework.authtoken import views
from rest_framework_jwt.views import obtain_jwt_token
# 引入Router
from rest_framework.routers import DefaultRouter


from goods.views import GoodsListView,CategoryViewSet,BannerViewSet,HotSearchWordsViewSet,IndexCategoryViewset
from users.views import SmsCodeViewset, UserViewset
from user_operation.views import UserFavset, LeavinngMessageViewset, UserAddressviewset
from trade.views import ShoppingCartviewset, OrderViewset,AlipayView


# 生成Router对象
router = DefaultRouter()

# 配置对应app的url
# 注意后面的base_bame不需要带了，在centos上运行项目会报错
# router.register('goods', GoodsListView, base_name='goods')
router.register(r'goods', GoodsListView, basename='goods')
router.register(r'categorys', CategoryViewSet, basename='categorys')
router.register(r'code', SmsCodeViewset, basename='code')
router.register(r'users', UserViewset, basename='users')
router.register(r'favs', UserFavset, basename='favs')
router.register(r'messages', LeavinngMessageViewset, basename='messages')
router.register(r'address', UserAddressviewset, basename='address')
router.register(r'shopcarts', ShoppingCartviewset, basename='shopcarts')
router.register(r'orders', OrderViewset, basename='orders')
router.register(r'banners', BannerViewSet, basename='banners')
router.register(r'hotsearchs', HotSearchWordsViewSet, basename='hotsearchs')
router.register(r'indexgoods', IndexCategoryViewset, basename='indexgoods')

from django.views.generic import TemplateView
urlpatterns = [
    url('xadmin/', xadmin.site.urls),

    # 富文本
    url(r'^media/(?P<path>.*)$', serve, {"document_root": MEDIA_ROOT}),
    url(r'^ueditor/', include('DjangoUeditor.urls')),

    #这个api-auth的URL不配置，那么在借口页面不出现登录按钮
    url(r'^api-auth/', include('rest_framework.urls')),
    # 根据上面Router，这里注册以下
    path('',include(router.urls)),

    url('index/', TemplateView.as_view(template_name='index.html'),name="index"),

    url('docs/',include_docs_urls(title='生鲜')),
    # drf自带的token认证模式
    # url(r'^api-token-auth/', views.obtain_auth_token),
    # 配置jwt认证接口
    url(r'^login/$', obtain_jwt_token),
    # 配置支付宝返回参数接受url
    url(r'^alipay/return/', AlipayView.as_view(), name="alipay"),


]
