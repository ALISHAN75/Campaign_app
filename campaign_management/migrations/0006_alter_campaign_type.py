# Generated by Django 3.2.7 on 2023-07-31 07:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('campaign_management', '0005_alter_campaign_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='campaign',
            name='type',
            field=models.CharField(choices=[('SMS', 'SMS'), ('Email', 'Email')], max_length=12),
        ),
    ]
