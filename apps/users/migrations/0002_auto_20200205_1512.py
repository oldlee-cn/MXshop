# Generated by Django 2.0 on 2020-02-05 15:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='moblie',
            field=models.CharField(blank=True, max_length=11, null=True, verbose_name='手机'),
        ),
    ]
