# Generated by Django 4.2 on 2023-05-02 13:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0003_alter_product_brand_brand_name_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchase_order',
            name='order_detail_file',
            field=models.FileField(null=True, upload_to='purchase_file/'),
        ),
        migrations.AddField(
            model_name='purchase_order',
            name='quantity',
            field=models.BigIntegerField(null=True),
        ),
        migrations.AddField(
            model_name='purchase_order',
            name='uploaded_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='purchase_order',
            name='value',
            field=models.BigIntegerField(null=True),
        ),
    ]
