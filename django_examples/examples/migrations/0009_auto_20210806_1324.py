# Generated by Django 2.2.5 on 2021-08-06 13:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('examples', '0008_auto_20210806_1131'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='date_entered',
            field=models.DateField(auto_now_add=True),
        ),
    ]