# Generated by Django 2.1.5 on 2019-03-31 21:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ofd_app', '0003_assign_permissions'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orderstatus',
            name='name',
        ),
    ]
