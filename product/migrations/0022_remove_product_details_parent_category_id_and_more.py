# Generated by Django 4.2 on 2023-07-26 07:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0021_product_details_parent_category_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product_details',
            name='parent_category_id',
        ),
        migrations.AddField(
            model_name='product_categories',
            name='parent_category_id',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='parent_category', to='product.product_categories'),
        ),
    ]