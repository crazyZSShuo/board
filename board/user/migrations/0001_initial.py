# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2018-08-09 13:32
from __future__ import unicode_literals

import common.utils
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import user.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('school', '0001_initial'),
        ('auth', '0008_alter_user_username_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=30, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('user_id', models.CharField(default=common.utils.get_unique_id, editable=False, max_length=16, unique=True, verbose_name='ID')),
                ('username', models.CharField(blank=True, default=common.utils.get_unique_id, max_length=24)),
                ('mobile', models.CharField(max_length=24, unique=True, verbose_name='手机号码')),
                ('name', models.CharField(max_length=32, null=True, verbose_name='姓名')),
                ('gender', models.CharField(choices=[('M', '男'), ('F', '女')], max_length=1, verbose_name='性别')),
                ('birthday', models.DateField(blank=True, null=True, verbose_name='生日')),
                ('address', models.CharField(blank=True, max_length=128, null=True, verbose_name='地址')),
                ('user_type', models.CharField(max_length=32, verbose_name='类别')),
                ('avatar', models.ImageField(default='user/avatar/default_avatar.png', max_length=128, upload_to=user.models.user_avatar_path, verbose_name='头像')),
            ],
            options={
                'verbose_name': '用户',
                'verbose_name_plural': '用户',
            },
            managers=[
                ('objects', user.models.UserProfileManager()),
            ],
        ),
        migrations.CreateModel(
            name='AuthToken',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(max_length=40, verbose_name='KEY')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('expire', models.DateTimeField(verbose_name='过期时间')),
            ],
            options={
                'verbose_name': 'Token',
                'verbose_name_plural': 'Tokens',
            },
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('operator_code', models.CharField(blank=True, default='', max_length=16, null=True, verbose_name='运行商code')),
                ('third_id', models.CharField(default='', max_length=16, verbose_name='THIRD_ID')),
                ('student_id', models.CharField(default=common.utils.get_unique_id, max_length=16, unique=True, verbose_name='ID')),
                ('name', models.CharField(max_length=32, verbose_name='姓名')),
                ('gender', models.CharField(choices=[('M', '男'), ('F', '女')], max_length=1, verbose_name='性别')),
                ('age', models.IntegerField(default=0, verbose_name='年龄')),
                ('mobile', models.CharField(max_length=14, verbose_name='学生卡号码')),
                ('clazz', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='students', to='school.Class', verbose_name='班级')),
            ],
            options={
                'verbose_name': '学生',
                'verbose_name_plural': '学生',
            },
        ),
        migrations.CreateModel(
            name='Teacher',
            fields=[
                ('userprofile_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('desc', models.CharField(blank=True, max_length=128, null=True, verbose_name='简述')),
                ('teacher_type', models.CharField(choices=[('teacher', '老师'), ('head_teacher', '班主任'), ('grade_director', '老师'), ('principal', '校长')], default='teacher', max_length=24, verbose_name='类别')),
                ('school', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='teachers', to='school.School', verbose_name='学校')),
            ],
            options={
                'verbose_name': '教师',
                'verbose_name_plural': '教师',
            },
            bases=('user.userprofile',),
            managers=[
                ('objects', user.models.TeacherManager()),
            ],
        ),
        migrations.AddField(
            model_name='authtoken',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='auth_token', to=settings.AUTH_USER_MODEL, verbose_name='User'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='groups',
            field=models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions'),
        ),
    ]