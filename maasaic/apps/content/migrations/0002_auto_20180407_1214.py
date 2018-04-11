# Generated by Django 2.0.3 on 2018-04-07 12:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='section',
            name='slug',
        ),
        migrations.AddField(
            model_name='section',
            name='html_id',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='page',
            name='target_page',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='edit_page', to='content.Page'),
        ),
        migrations.AlterField(
            model_name='section',
            name='name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]