# Generated by Django 4.2 on 2023-05-08 12:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0006_alter_product_details_metadata'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product_brand',
            name='brand_desc',
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name='product_categories',
            name='category_desc',
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name='product_stock',
            name='checked_stock',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='product_stock',
            name='unchecked_stock',
            field=models.IntegerField(null=True),
        ),
    ]
