# Generated by Django 3.2.6 on 2022-06-11 08:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0008_forum_deleted'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='avatar',
            field=models.ImageField(default='', upload_to='D:\\ПИТОНН\\CookHelper\\cookhelper\\media/'),
        ),
    ]
