# Generated by Django 2.1.7 on 2019-05-19 16:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('atriacalendar', '0010_atriaoccurrence'),
    ]

    operations = [
        migrations.AddField(
            model_name='relationtype',
            name='is_org_relation',
            field=models.BooleanField(default=False),
        ),
    ]
