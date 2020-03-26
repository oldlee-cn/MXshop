from datetime import datetime

from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.


class UserProfile(AbstractUser):
    """
    用户
    """
    name = models.CharField(max_length=30, null=True, blank=True, verbose_name='姓名', default='',help_text="用户")
    birthday = models.DateTimeField(null=True, verbose_name='出生日期', blank=True)
    moblie = models.CharField(null=True, blank=True,max_length=11, verbose_name='手机',help_text="手机号")
    gender = models.CharField(max_length=6, verbose_name='性别', choices=(('male','男'), ('female','女')), default='female')
    email = models.CharField(max_length=100, verbose_name='邮箱', null=True, blank=True)

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class VerifyCode(models.Model):
    """
    验证码
    """
    code = models.CharField(max_length=10, verbose_name='验证码')
    moblie = models.CharField(max_length=11, verbose_name='手机')
    add_time = models.DateTimeField(default=datetime.now, verbose_name='添加时间')

    class Meta:
        verbose_name = '验证码'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.code
