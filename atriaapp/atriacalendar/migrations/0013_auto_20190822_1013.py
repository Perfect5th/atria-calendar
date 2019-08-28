# Generated by Django 2.1.7 on 2019-08-22 10:13

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('atriacalendar', '0012_atriaoccurrence_published'),
    ]

    operations = [
        migrations.CreateModel(
            name='AtriaVolunteerOpportunity',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.TextField(blank=True, max_length=4000)),
                ('description', models.TextField(blank=True, max_length=4000)),
                ('start_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('date_added', models.DateTimeField(default=django.utils.timezone.now)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='atriacalendar.AtriaEvent')),
            ],
        ),
        migrations.RemoveField(
            model_name='atriaeventattendance',
            name='event',
        ),
        migrations.AddField(
            model_name='atriaeventattendance',
            name='occurrence',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='atriacalendar.AtriaOccurrence'),
        ),
        migrations.AlterField(
            model_name='atriaeventattendance',
            name='notes',
            field=models.TextField(blank=True, max_length=4000, null=True),
        ),
        migrations.AlterField(
            model_name='atriaeventattendance',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='atriaeventattendance',
            name='volunteer_opportunity',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='atriacalendar.AtriaVolunteerOpportunity'),
        ),
    ]
