# Generated by Django 5.1.6 on 2025-03-07 01:37

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0008_remove_transaction_description_transaction_category_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='income',
            name='category',
        ),
        migrations.RemoveField(
            model_name='expense',
            name='category',
        ),
        migrations.RemoveField(
            model_name='expense',
            name='user',
        ),
        migrations.RemoveField(
            model_name='income',
            name='user',
        ),
        migrations.RemoveField(
            model_name='transactionhistory',
            name='user',
        ),
        migrations.AddField(
            model_name='transaction',
            name='basic_expense',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='finance.basicexpense'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='income_source',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='finance.incomesource'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='savings_investment',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='finance.savingsinvestment'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='wish_expense',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='finance.wishexpense'),
        ),
        migrations.DeleteModel(
            name='Category',
        ),
        migrations.DeleteModel(
            name='Expense',
        ),
        migrations.DeleteModel(
            name='Income',
        ),
        migrations.DeleteModel(
            name='TransactionHistory',
        ),
    ]
