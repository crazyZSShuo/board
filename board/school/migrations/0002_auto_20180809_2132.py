# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2018-08-09 13:32
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('user', '0001_initial'),
        ('school', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='teacherclassrelation',
            name='teacher',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='class_relations', to='user.Teacher', verbose_name='教师'),
        ),
        migrations.AddField(
            model_name='school',
            name='principal',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='principal', to='user.Teacher', verbose_name='校长'),
        ),
        migrations.AddField(
            model_name='class',
            name='school',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='classes', to='school.School', verbose_name='学校'),
        ),
        migrations.AddField(
            model_name='class',
            name='teachers',
            field=models.ManyToManyField(related_name='classes', through='school.TeacherClassRelation', to='user.Teacher', verbose_name='教师'),
        ),
        migrations.AlterUniqueTogether(
            name='teacherclassrelation',
            unique_together=set([('teacher', 'clazz')]),
        ),
    ]