# Generated by Django 4.2 on 2023-07-06 07:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0017_product_qc_status_qc_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product_qc_status',
            name='qc_code',
            field=models.CharField(default='FRH', max_length=3),
        ),
    ]
