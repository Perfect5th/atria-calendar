# Generated by Django 2.0.9 on 2018-12-16 08:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('atriacalendar', '0002_auto_20181108_0018'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='atrianote',
            name='note_ptr',
        ),
        migrations.DeleteModel(
            name='AtriaNote',
        ),
    ]
