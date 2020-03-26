# -*- coding: utf-8 -*-
__author__ = 'oldlee'
__date__ = '2020-02-05 14:55'

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model

User = get_user_model()

# 这是一个装饰器，注意语法
@receiver(post_save, sender=User)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        password = instance.password
        instance.set_password(password)
        instance.save()

# 以上这一段也可以代替serializer中的重写create来完成密码的创建工作，以此来保持serializers文件的优雅



    #上面代码安成后，我们还需要做一下配置
    # 那就是在app.py文件中，重载以下的函数
    #
    #     def ready(self):
    #         import users.signals
