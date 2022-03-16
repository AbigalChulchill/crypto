# Generated by Django 3.2 on 2022-02-28 20:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0007_profiletrading'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProfileTradingOrders',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_trading_coin_quantity', models.CharField(max_length=100)),
                ('second_trading_coin_quantity', models.CharField(max_length=100)),
                ('trading', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='profiles.profiletrading')),
                ('trading_order_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='profiles.tradingordertype')),
            ],
        ),
    ]