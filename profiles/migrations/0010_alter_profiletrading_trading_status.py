# Generated by Django 3.2 on 2022-03-01 21:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0009_profiledirectorder_limit_order_quantity'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profiletrading',
            name='trading_status',
            field=models.CharField(choices=[('0', 'RUN'), ('1', 'COMPLETE')], default=0, max_length=2),
        ),
    ]
