# Generated by Django 3.2.7 on 2023-06-09 14:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('modal_examples', '0010_companycolour'),
    ]

    operations = [
        migrations.AddField(
            model_name='note',
            name='completed',
            field=models.BooleanField(default=False),
        ),
    ]
