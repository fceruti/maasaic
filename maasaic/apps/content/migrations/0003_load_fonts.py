# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-04-10 20:04
from __future__ import unicode_literals

from django.db import migrations
from django.db.models import Sum
import os
from sys import path
from django.core import serializers

fixture_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../data'))
fixture_filename = 'fonts.json'


def load_fonts(apps, schema_editor):
    fixture_file = os.path.join(fixture_dir, fixture_filename)

    fixture = open(fixture_file, 'rb')
    objects = serializers.deserialize('json', fixture, ignorenonexistent=True)
    for obj in objects:
        obj.save()
    fixture.close()


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0002_auto_20180503_0219'),
    ]

    operations = [
        migrations.RunPython(load_fonts),
    ]
