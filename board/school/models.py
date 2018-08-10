# coding=utf-8

import binascii
import os
from datetime import date, datetime

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.db import models
from jsonfield import JSONCharField

from common.utils import cnum, get_unique_id
from user.models import Teacher, Student


def get_default_role():
    return []


def school_logo_path(instance, filename):
    return 'school/logo/{0}{1}'.format(binascii.hexlify(os.urandom(20)).decode(), os.path.splitext(filename)[1])


class School(models.Model):
    school_id = models.CharField(default=get_unique_id, max_length=16, unique=True, editable=False, verbose_name='ID')
    name = models.CharField(max_length=64, verbose_name='名称')
    province = models.CharField(max_length=32, default="", verbose_name='省份')
    city = models.CharField(max_length=32, verbose_name='城市')
    district = models.CharField(max_length=32, verbose_name='行政区')
    address = models.CharField(max_length=128, verbose_name='详细地址')
    logo = models.ImageField(max_length=128, upload_to=school_logo_path, verbose_name='LOGO')
    desc = models.TextField(verbose_name='简介', null=True, blank=True)
    principal = models.OneToOneField(to=Teacher, limit_choices_to={'teacher_type': 'principal'},
                                     related_name='principal',
                                     null=True, blank=True, verbose_name='校长', on_delete=models.SET_NULL)
    create = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '学校'
        verbose_name_plural = verbose_name


class TeacherPosition(models.Model):
    name = models.CharField(max_length=128, verbose_name='名称')
    type = models.CharField(default='0', max_length=8, verbose_name='老师类型')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '教师职位'
        verbose_name_plural = verbose_name


class TeacherClassRelation(models.Model):
    teacher = models.ForeignKey(to='user.Teacher', related_name='class_relations', verbose_name='教师')
    clazz = models.ForeignKey(to='Class', related_name='teacher_relations', verbose_name='班级')
    position = models.ManyToManyField(to=TeacherPosition, verbose_name='位置-废弃')
    role = JSONCharField(default=get_default_role, max_length=32, verbose_name='角色')

    def __str__(self):
        return '%s-%s-%s' % (self.teacher.name, self.clazz.name, self.position)

    class Meta:
        verbose_name = '教师班级关系'
        verbose_name_plural = verbose_name
        db_table = 'school_teacher_class_relation'
        unique_together = ('teacher', 'clazz')


class Class(models.Model):
    class_id = models.CharField(default=get_unique_id, max_length=16, unique=True, editable=False, verbose_name='ID')
    name = models.CharField(max_length=32, null=True, blank=True, verbose_name='名称')
    desc = models.TextField(verbose_name='简介', null=True, blank=True)
    create = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    teachers = models.ManyToManyField(to='user.Teacher', through=TeacherClassRelation, related_name='classes',
                                      verbose_name='教师')
    index_of_grade = models.IntegerField(default=1, verbose_name='班级序号')
    base_index_of_grade = models.IntegerField(default=0, verbose_name='班级起始index')
    grade_index = models.IntegerField(default=1, verbose_name='年级序号')
    start = models.DateField(default=date(2016, 7, 1), verbose_name='入学日期')
    school = models.ForeignKey(to=School, related_name='classes', null=True, verbose_name='学校')

    @property
    def canonical_name(self):
        return '%s年级%s班' % (cnum(self.grade_index), cnum(self.index_of_grade))

    @property
    def current_grade_index(self):
        now = datetime.now()
        years = now.year - self.start.year
        if now.month > self.start.month:
            years += 1
        elif now.month == self.start.month and now.day >= self.start.day:
            years += 1
        if years <= 0:
            years = 1
        return years

    @property
    def new_canonical_name(self):
        return '%s级%s班' % (self.start.year + self.base_index_of_grade, cnum(self.index_of_grade))

    def __str__(self):
        return '{}/{}'.format(self.canonical_name or self.name, self.school)

    def get_im_group_users(self):
        users = []
        users.extend([str(p.im_user_id) for p in self.teachers.all() if p and p.im_user_id])
        return users

    @property
    def student_count(self):
        return self.students.count()

    class Meta:
        verbose_name = '班级'
        verbose_name_plural = verbose_name
        ordering = ['-start', 'index_of_grade']


fs = FileSystemStorage(location=settings.MEDIA_ROOT)
