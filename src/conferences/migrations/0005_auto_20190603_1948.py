# Generated by Django 2.0.9 on 2019-06-03 16:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('conferences', '0004_auto_20190603_1819'),
    ]

    operations = [
        migrations.AlterField(
            model_name='conference',
            name='sections',
            field=models.ManyToManyField(null=True, to='conferences.Section'),
        ),
    ]