# Generated by Django 4.2.11 on 2024-04-14 20:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ReceiptHub', '0008_receipt_total_amount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='receipt',
            name='total_amount',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
