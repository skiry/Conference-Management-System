# Generated by Django 2.0.9 on 2019-05-29 15:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('conferences', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Submission',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('abstract', models.CharField(max_length=255)),
                ('fullPaper', models.CharField(max_length=25500)),
                ('metaInfo', models.CharField(max_length=10000)),
                ('submitter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='conferences.Actor')),
            ],
        ),
    ]