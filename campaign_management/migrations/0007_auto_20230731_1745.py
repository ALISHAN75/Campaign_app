# Generated by Django 3.2.7 on 2023-07-31 12:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('campaign_management', '0006_alter_campaign_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contacts',
            name='address',
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
        migrations.AlterField(
            model_name='contacts',
            name='city',
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
        migrations.AlterField(
            model_name='contacts',
            name='name',
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
    ]
