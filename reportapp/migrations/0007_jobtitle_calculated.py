# Generated by Django 4.1.3 on 2023-01-07 12:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reportapp', '0006_remove_reportdata_share_ready'),
    ]

    operations = [
        migrations.AddField(
            model_name='jobtitle',
            name='calculated',
            field=models.BooleanField(default=True, verbose_name='Учитывается в расчете'),
        ),
    ]