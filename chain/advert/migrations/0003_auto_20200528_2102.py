# Generated by Django 3.0.2 on 2020-05-28 21:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('advert', '0002_auto_20200522_1523'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='content',
            options={'ordering': ('-datetime',), 'verbose_name': '广告表', 'verbose_name_plural': '广告表'},
        ),
    ]
