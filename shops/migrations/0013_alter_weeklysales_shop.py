# Generated by Django 4.1.3 on 2022-11-03 11:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shops', '0012_alter_fruit_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='weeklysales',
            name='shop',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shops.shop'),
        ),
    ]