from django.shortcuts import render

# Create your views here.

from rest_framework.permissions import IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.authentication import SessionAuthentication
from rest_framework import viewsets
from rest_framework import mixins
from rest_framework.response import Response
from django.shortcuts import redirect

from .serializers import ShoppingCartSerializer,ShopcartDetailSerializer,OrderSerializer,OrderDetailSerializer
from .models import ShoppingCart,OrderInfo,OrderGoods
from utils.permissions import IsOwnerOrReadOnly
from utils.alipayapi import AliPay
from MXshop.settings import private_key_path,ali_pub_key_path

from datetime import datetime

class ShoppingCartviewset(viewsets.ModelViewSet):
    """管理购物车
    list:
        购物车商品
    create:
        添加购物车
    delete:
        删除购物车
    update:
        更新购物车
    """
    permission_classes = (IsAuthenticated,IsOwnerOrReadOnly)
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    serializer_class = ShoppingCartSerializer
    lookup_field = "goods"

    def perform_create(self, serializer):
        shop_cart = serializer.save()
        goods = shop_cart.goods
        goods.goods_num -= shop_cart.nums
        # goods.sold_num += shop_cart.nums      #加入购物车增加销量
        goods.save()

    def perform_destroy(self, instance):
        goods = instance.goods
        goods.goods_num += instance.nums
        # goods.sold_num -= instance.nums      #加入购物车增加销量
        goods.save()
        instance.delete()

    def perform_update(self, serializer):
        #取出购物车之前对应商品的记录
        existed_record = ShoppingCart.objects.get(id=serializer.instance.id)
        #取出之前商品的数量
        existed_nums = existed_record.nums
        #取出新保存的商品的数量
        saved_record = serializer.save()
        # 新保存的减去之前的
        num = saved_record.nums-existed_nums
        #取到新保存的对应的商品
        goods = saved_record.goods
        #使用上面计算的数量对当前商品的数量做计算
        goods.goods_num -= num
        # goods.sold_num += num       #加入购物车增加销量
        # 然后保存
        goods.save()


    def get_serializer_class(self):
        if self.action == "list":
            return ShopcartDetailSerializer
        else:
            return ShoppingCartSerializer

    # 下面的的作用是只获取当前用户，也就是只返回当前用户的数据
    def get_queryset(self):
        return ShoppingCart.objects.filter(user = self.request.user)


class OrderViewset( mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.CreateModelMixin,mixins.DestroyModelMixin,viewsets.GenericViewSet):
    """
    订单管理：
    list：
        订单列表
    delete：
        订单删除
    create:
        订单创建
    """
    permission_classes =(IsAuthenticated, IsOwnerOrReadOnly)
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    serializer_class = OrderSerializer

    def get_serializer_class(self):
        if self.action == "retrieve":
            return OrderDetailSerializer
        return OrderSerializer

    def get_queryset(self):
        return OrderInfo.objects.filter(user=self.request.user)

    #这个函数在用户注册的view里也重写过，他的原作用是对serializer的model进行保存，也就是class Meta：model= 某个Model
    # 这里，这个函数保存的就是   这个model，我们把保存结果赋值给order
    def perform_create(self, serializer):
        order = serializer.save()
        #取出当前用户下的所有购物车记录
        shop_carts = ShoppingCart.objects.filter(user=self.request.user)
        #遍历购物车记录
        for shop_cart in shop_carts:
            order_goods = OrderGoods()    #实例化订单商品model
            order_goods.goods = shop_cart.goods     #将购物车商品赋值给订单里商品
            order_goods.goods_num = shop_cart.nums      #将购物车商品数量赋值给订单商品
            order_goods.order = order       #将订单信息赋值给订单商品的订单信息
            order_goods.save()          #保存

            shop_cart.delete()      #然后清除购物车对应的商品
        return order    #返回order


from rest_framework.views import APIView
#这里由于是处理支付宝的参数，所有没有合适的model，直接继承最底层的APIView
class AlipayView(APIView):
    def get(self,request):
        """
        处理支付宝的return_url的返回
        用户在支付宝支付后，支付宝同步跳转的网页
        :param request:
        :return:
        """
        processed_dict = {}
        for key, value in request.GET.items():
            processed_dict[key] = value

        sign = processed_dict.pop('sign', None)  # 剔除里面的sign
        # 实例化alipay接口实例
        alipay = AliPay(
            appid="2021001129619051",
            app_notify_url="http://47.101.69.87:8000/alipay/return/",
            app_private_key_path=private_key_path,
            alipay_public_key_path=ali_pub_key_path,  # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            debug=False,  # 默认False,
            return_url="http://47.101.69.87:8000/alipay/return/"
        )
        # 验证sign，是否是支付宝请求过来的数据
        verify_re = alipay.verify(processed_dict, sign)

        # 如果验证通过，即为True，就取出返回的数据字段
        if verify_re is True:
            order_sn = processed_dict.get('out_trade_no', None)
            trade_no = processed_dict.get('trade_no', None)
            # trade_status = processed_dict.get('trade_status', None)

            existed_orders = OrderInfo.objects.filter(order_sn=order_sn)
            for existed_order in existed_orders:
                # existed_order.pay_status = trade_status
                existed_order.trade_no = trade_no
                existed_order.pay_time = datetime.now()
                existed_order.save()

            # 设置成功后跳转到index，并且设置cookie和过期时间，短一点
            # 并且nexPath=pay
            response = redirect("index")
            response.set_cookie("nextPath","pay",max_age=3)     #这里vue接受到cookie并且nextPath=pay，就会跳转指定页面
            return response     #最后返回
        else:
            # 如果不成功，就只跳转首页index，不设置cookie
            response= redirect("index")
            return response
    def post(self,request):
        """
        处理支付宝的notify_url的返回
        用户在支付宝支付后，支付宝异步跳转的网页，一般用于创建支付订单后退出，重新进入
        :param request:
        :return:
        """
        # 这里支付宝在做异步回调的时候通过post方式将参数传回
        # 我们取出参数，并全部存在processed_dict里
        processed_dict = {}
        for key,value in request.POST.items():
            processed_dict[key] = value

        sign = processed_dict.pop('sign',None)  #剔除里面的sign
        # 实例化alipay接口实例
        alipay = AliPay(
            appid="2021001129619051",
            app_notify_url="http://47.101.69.87:8000/alipay/return/",
            app_private_key_path=private_key_path,
            alipay_public_key_path=ali_pub_key_path,  # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            debug=False,  # 默认False,
            return_url="http://47.101.69.87:8000/alipay/return/"
        )
        # 验证sign，是否是支付宝请求过来的数据
        verify_re = alipay.verify(processed_dict,sign)

        # 如果验证通过，即为True，就取出返回的数据字段
        if verify_re is True:
            order_sn = processed_dict.get("out_trade_no",None)
            trade_no = processed_dict.get("trade_no",None)
            trade_status = processed_dict.get("trade_status",None)

            # 从数据中取出对应订单号的数据：
            existed_orders = OrderInfo.objects.filter(order_sn=order_sn)
            # 遍历，将支付宝返回的数据复制给数据库中的对应的订单信息
            for existed_order in existed_orders:

                #对商品销量的保存，在成功返回支付宝数据后：
                #从数据中取出对应订单号数据中的商品数据
                order_goods = existed_order.goods.all()
                for order_good in order_goods:  #遍历，因为订单中可能不止一个商品
                    goods = order_good.goods   #取出对应的商品
                    goods.sold_num += order_good.goods_num     #然后将订单中对应的商品数量加到对应商品的销量上
                    goods.save()        #保存

                existed_order.pay_status = trade_status     #赋值订单状态
                existed_order.trade_no = trade_no           #赋值支付宝的交易号
                existed_order.pay_time = datetime.now()     #复制支付时间
                # 最后保存
                existed_order.save()

                # 最后还需要返回一个success给支付宝
                # 这里如果不返回这个success，支付宝就不停的向我们的指定的接口发送数据
                return Response('success')





