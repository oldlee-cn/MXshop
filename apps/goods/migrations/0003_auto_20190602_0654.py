# Generated by Django 2.0 on 2019-06-01 22:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('goods', '0002_hotsearchwords_indexad'),
    ]

    operations = [
        migrations.AddField(
            model_name='goodscategorybrand',
            name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='goods.GoodsCategory', verbose_name='商品类目'),
        ),
        migrations.AlterField(
            model_name='goodscategory',
            name='category_type',
            field=models.CharField(choices=[('1', '一级类目'), ('2', '二级类目'), ('3', '三级类目')], help_text='类目级别', max_length=50, verbose_name='类目级别'),
        ),
    ]
