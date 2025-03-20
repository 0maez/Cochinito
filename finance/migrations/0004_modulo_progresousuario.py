# Generated by Django 5.1.6 on 2025-03-20 21:07

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0003_remove_transaction_category_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Modulo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo', models.CharField(max_length=255)),
                ('descripcion', models.TextField()),
                ('video_titulo', models.CharField(max_length=255)),
                ('video_url', models.URLField()),
                ('ejercicio', models.TextField()),
                ('orden', models.IntegerField(unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='ProgresoUsuario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('completado', models.BooleanField(default=False)),
                ('modulo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='finance.modulo')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
