# Generated by Django 4.2.11 on 2024-04-14 09:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ReceiptHub', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Receipt',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
    ]
