# Generated by Django 2.0 on 2021-01-06 15:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('voting', '0005_auto_20210106_1519'),
    ]

    operations = [
        migrations.AlterField(
            model_name='yesorno',
            name='choice',
            field=models.CharField(blank=True, choices=[('Y', 'Yes'), ('N', 'No')], max_length=1),
        ),
    ]