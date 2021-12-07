# Generated by Django 3.2.7 on 2021-12-07 21:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('modal_examples', '0009_auto_20210806_1324'),
    ]

    operations = [
        migrations.CreateModel(
            name='CompanyColour',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('colour', models.CharField(max_length=10)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='modal_examples.company')),
            ],
        ),
    ]
