# Generated by Django 3.2.16 on 2023-12-20 07:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0006_addcomment'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='post',
            options={'verbose_name': 'публикация', 'verbose_name_plural': 'Публикации'},
        ),
    ]
