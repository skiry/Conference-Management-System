# Generated by Django 2.0.9 on 2019-06-03 14:13

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('conferences', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='conference',
            name='bidding_date',
            field=models.DateField(default=datetime.datetime(2019, 6, 3, 14, 13, 45, 897055, tzinfo=utc)),
            preserve_default=False,
        ),
    ]
