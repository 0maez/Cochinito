# Generated by Django 5.1.6 on 2025-03-07 03:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0009_remove_income_category_remove_expense_category_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
    ]
