
from rest_framework import mixins
from rest_framework import filters
from rest_framework.pagination import PageNumberPagination
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework_extensions.cache.mixins import CacheResponseMixin
from rest_framework.throttling import AnonRateThrottle,UserRateThrottle

from .serializers import GoodsSerializer,CategroySerializer,BannerSerializer,HotWordsSerializer,IndexCategorySerializer
from django_filters.rest_framework import DjangoFilterBackend
from .models import Goods,GoodsCategory,Banner,HotSearchWords
from .filters import GoodsFilter


# 深度自定义数据的分页样式
class GoodsSetPagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 100
    # 指定url的后缀的自定义名称"page=2"，比如第三页就是"http://127.0.0.1:8000/goods/?page=3",
    page_query_param = 'page'


# class GoodsListView(mixins.ListModelMixin, generics.GenericAPIView):配合mixin形成各种组合，如ListAPIview

# 这里如果直接继承generics下面的ListApiView，就可以把下面的重载get函数也省略了
# class GoodsListView(mixins.ListModelMixin,generics.ListAPIView):

# 使用viewsets又集成了URL配置：as_view和.action各种功能
# class GoodsListView(mixins.ListModelMixin,viewsets.GenericViewSet):
# 而viewsets还有很多组合，如下面这个，就包含了GenericViewSet和mixins.ListModelMixin
class GoodsListView(CacheResponseMixin,mixins.ListModelMixin,mixins.RetrieveModelMixin,viewsets.GenericViewSet):
    """
    oldlee
    """
    throttle_classes = (UserRateThrottle,AnonRateThrottle)
    queryset = Goods.objects.all()
    serializer_class = GoodsSerializer

    # 这里调用分页样式的类，也就是上面的GoodsSetPagination
    pagination_class = GoodsSetPagination

    # 进行过滤，上面要导入DjangoFilterBackend，项目要安装和settings.py里要配置"django_filters"
    # 上面导入rest_framework下的filers，然后下面就可以注册引用filters.SearchFilter,包括filters.OrderingFilter也是，上面import后，这里注册就可以了

    filter_backends = [DjangoFilterBackend,filters.SearchFilter,filters.OrderingFilter]
    filter_class = GoodsFilter
    filterset_fields = ['name', 'market_price']    #过滤
    # 下面这里就可以添加需要进行搜索的字段：name，goods_desc等
    search_fields = ['name','goods_desc']
    # ordering_fields = '__all__'   排序
    ordering_fields = ['sold_num', 'shop_price']


    # 然后重载get函数，他会调用list函数，自动序列化，如果这里不对get进行重载的话，mixin就默认我们不调用get请求
    # def get(self, request, *args, **kwargs):
    #     return self.list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        #实现商品点击数的修改，重写retrieve方法，每次读取就给click_num+1并保存
        instance.click_num +=1
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

# 添加继承mixins.RetrieveModelMixin，就可以获取某一个分类的详情信息，不是全部的，是单个的，配置他之后，连url都可以不用配置，直接在分类的url后面加上分类id即可获取
# 注意，这里只有CategoryViewSet继承了mixins.RetrieveModelMixin，所以，只有一级分类才可以直接在后面加id获取
class CategoryViewSet(mixins.ListModelMixin,mixins.RetrieveModelMixin,viewsets.GenericViewSet):
    """
    桑品分类说明
    """
    queryset = GoodsCategory.objects.filter(category_type=1)
    serializer_class = CategroySerializer


class HotSearchWordsViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    #排序，倒序
    queryset = HotSearchWords.objects.all().order_by("-index")
    serializer_class = HotWordsSerializer


class BannerViewSet(mixins.ListModelMixin,viewsets.GenericViewSet):
    #排序，正序
    queryset = Banner.objects.all().order_by("index")
    serializer_class = BannerSerializer


class IndexCategoryViewset(mixins.ListModelMixin,viewsets.GenericViewSet):
    #这里的queryset，不使用all()，只需要使用filter()取出在导航的分类即可,可以多次限定使用name_in=["生鲜食品","酒水饮料"]
    queryset = GoodsCategory.objects.filter(is_tab=True)
    serializer_class = IndexCategorySerializer