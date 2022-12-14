# Generated by Django 4.1.3 on 2022-11-03 11:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shops', '0010_alter_shop_year_opened'),
    ]

    operations = [
        migrations.CreateModel(
            name='Fruit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
            ],
        ),
        migrations.AlterField(
            model_name='shop',
            name='code',
            field=models.CharField(max_length=10, unique=True),
        ),
        migrations.CreateModel(
            name='WeeklySales',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('shop', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='shops.shop')),
            ],
        ),
        migrations.CreateModel(
            name='ShopOverheads',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('overhead_type', models.CharField(choices=[('PERS', 'personnel'), ('PREM', 'premises'), ('OTHER', 'other overheads')], max_length=30)),
                ('cost', models.IntegerField()),
                ('weekly_sales', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shops.weeklysales')),
            ],
        ),
        migrations.CreateModel(
            name='FruitSales',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('units_bought', models.IntegerField()),
                ('cost_per_unit', models.DecimalField(decimal_places=2, max_digits=6)),
                ('units_sold', models.IntegerField()),
                ('price_per_unit', models.DecimalField(decimal_places=2, max_digits=6)),
                ('units_waste', models.IntegerField()),
                ('fruit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shops.fruit')),
                ('weekly_sales', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shops.weeklysales')),
            ],
        ),
    ]
