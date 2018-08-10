# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2018-08-09 13:32
from __future__ import unicode_literals

import common.utils
import datetime
from django.db import migrations, models
import django.db.models.deletion
import jsonfield.fields
import school.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Class',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('class_id', models.CharField(default=common.utils.get_unique_id, editable=False, max_length=16, unique=True, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=32, null=True, verbose_name='名称')),
                ('desc', models.TextField(blank=True, null=True, verbose_name='简介')),
                ('create', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('index_of_grade', models.IntegerField(default=1, verbose_name='班级序号')),
                ('base_index_of_grade', models.IntegerField(default=0, verbose_name='班级起始index')),
                ('grade_index', models.IntegerField(default=1, verbose_name='年级序号')),
                ('start', models.DateField(default=datetime.date(2016, 7, 1), verbose_name='入学日期')),
            ],
            options={
                'verbose_name': '班级',
                'verbose_name_plural': '班级',
                'ordering': ['-start', 'index_of_grade'],
            },
        ),
        migrations.CreateModel(
            name='School',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('school_id', models.CharField(default=common.utils.get_unique_id, editable=False, max_length=16, unique=True, verbose_name='ID')),
                ('name', models.CharField(max_length=64, verbose_name='名称')),
                ('province', models.CharField(default='', max_length=32, verbose_name='省份')),
                ('city', models.CharField(max_length=32, verbose_name='城市')),
                ('district', models.CharField(max_length=32, verbose_name='行政区')),
                ('address', models.CharField(max_length=128, verbose_name='详细地址')),
                ('logo', models.ImageField(max_length=128, upload_to=school.models.school_logo_path, verbose_name='LOGO')),
                ('desc', models.TextField(blank=True, null=True, verbose_name='简介')),
                ('create', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
            ],
            options={
                'verbose_name': '学校',
                'verbose_name_plural': '学校',
            },
        ),
        migrations.CreateModel(
            name='TeacherClassRelation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', jsonfield.fields.JSONCharField(default=school.models.get_default_role, max_length=32, verbose_name='角色')),
                ('clazz', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='teacher_relations', to='school.Class', verbose_name='班级')),
            ],
            options={
                'verbose_name': '教师班级关系',
                'verbose_name_plural': '教师班级关系',
                'db_table': 'school_teacher_class_relation',
            },
        ),
        migrations.CreateModel(
            name='TeacherPosition',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128, verbose_name='名称')),
                ('type', models.CharField(default='0', max_length=8, verbose_name='老师类型')),
            ],
            options={
                'verbose_name': '教师职位',
                'verbose_name_plural': '教师职位',
            },
        ),
        migrations.AddField(
            model_name='teacherclassrelation',
            name='position',
            field=models.ManyToManyField(to='school.TeacherPosition', verbose_name='位置-废弃'),
        ),
    ]