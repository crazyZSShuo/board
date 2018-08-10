# coding=utf-8

import binascii
import os
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.files.storage import FileSystemStorage
from django.db import models, connection
from django.db.models.signals import post_save
from django.utils.timezone import now

from common.utils import get_unique_id, generate_md5


def user_avatar_path(instance, filename):
    return 'user/avatar/{0}{1}'.format(binascii.hexlify(os.urandom(20)).decode(), os.path.splitext(filename)[1])


GENDER_CHOICE = (
    ('M', '男'),
    ('F', '女')
)

USER_TYPE = (
    ('P', '家长'),
    ('T', '教师'),
)

TEACHER_TYPE = (
    ('teacher', '老师'),
    ('head_teacher', '班主任'),
    ('grade_director', '老师'),
    ('principal', '校长')
)
TEACHER_TYPE_MAP = dict(TEACHER_TYPE)


class UserProfileManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, mobile, password, **extra_fields):
        if not mobile:
            raise ValueError('The given mobile must be set')
        user = self.model(mobile=mobile, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, mobile, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(mobile, password, **extra_fields)

    def create_superuser(self, mobile, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(mobile, password, **extra_fields)


class TeacherManager(UserProfileManager):
    def get_queryset(self):
        return super(TeacherManager, self).get_queryset().filter(user_type__contains='T')

    def create(self, **kwargs):
        mobile = kwargs.get('mobile')
        try:
            user = UserProfile.objects.get(mobile=mobile)
            if Teacher.objects.filter(mobile=mobile).count() != 0:
                user.user_type = 'T'
                user.save()
                cursor = connection.cursor()
                cursor.execute("INSERT INTO user_teacher VALUES (%s, NULL, %s, NULL , NULL, NULL, %s);",
                               [user.pk, 'teacher', get_unique_id()])
                return Teacher.objects.get(mobile=mobile)
            else:
                return super().create(**kwargs)
        except UserProfile.DoesNotExist:
            return super().create(**kwargs)


class UserProfile(AbstractUser):
    '''
    Customized Django USER model
    User type:  T -> Teacher
                P -> Parent
                SA -> SchoolAdmin
                VSA -> Vice SchoolAdmin
                SU -> SYSADMIN

    '''
    user_id = models.CharField(default=get_unique_id, max_length=16, unique=True, editable=False, verbose_name='ID')
    username = models.CharField(max_length=24, default=get_unique_id, blank=True)
    mobile = models.CharField(max_length=24, unique=True, verbose_name='手机号码')
    # nick_name = models.CharField(max_length=64, null=True, blank=True, verbose_name='昵称')
    name = models.CharField(max_length=32, null=True, verbose_name='姓名')
    gender = models.CharField(max_length=1, choices=GENDER_CHOICE, verbose_name='性别')
    birthday = models.DateField(null=True, blank=True, verbose_name='生日')
    address = models.CharField(max_length=128, null=True, blank=True, verbose_name='地址')
    user_type = models.CharField(max_length=32, verbose_name='类别')
    avatar = models.ImageField(default='user/avatar/default_avatar.png',
                               max_length=128, upload_to=user_avatar_path, verbose_name='头像')
    objects = UserProfileManager()

    USERNAME_FIELD = 'mobile'
    REQUIRED_FIELDS = []

    __original_avatar = None

    def __init__(self, *args, **kwargs):
        super(UserProfile, self).__init__(*args, **kwargs)
        self.__original_avatar = self.avatar

    def save(self, *args, **kwargs):
        # if self.avatar != self.__original_avatar:
        #     # avatar changed
        #     from user.tasks import refresh_im_user_info
        #     refresh_im_user_info(self.pk)
        #     pass
        super(UserProfile, self).save(*args, **kwargs)
        self.__original_avatar = self.avatar

    @property
    def nick_name(self):
        name = list()
        if self.is_teacher:
            name.append(self.teacher.nick_name)
        if name:
            return '/'.join(name)
        return self.mobile

    @property
    def is_teacher(self):
        return 'T' in self.user_type

    @property
    def is_school_admin(self):
        return 'SA' in self.user_type

    @property
    def is_vice_school_admin(self):
        return 'VSA' in self.user_type

    @property
    def is_system_admin(self):
        return 'SU' in self.user_type

    @property
    def is_customer(self):
        return 'C' in self.user_type

    def __str__(self):
        return self.nick_name or self.mobile

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = verbose_name


# Teacher Model extend UserProfile
class Teacher(UserProfile):
    desc = models.CharField(max_length=128, verbose_name='简述', null=True, blank=True)
    teacher_type = models.CharField(max_length=24, choices=TEACHER_TYPE, default='teacher', verbose_name='类别')
    school = models.ForeignKey(to='school.School', related_name='teachers', null=True, blank=True, verbose_name='学校')

    objects = TeacherManager()

    def save(self, *args, **kwargs):
        if self.user_type:
            roles = self.user_type.split(',')
            self.user_type = ','.join(roles if 'T' in roles else roles.append('T'))
        else:
            self.user_type = 'T'
        if self.teacher_type == 'grade_director':
            user_type = self.user_type.split(',')
            if 'VSA' not in user_type:
                user_type.append('VSA')
            self.user_type = ','.join(user_type)
        else:
            user_type = self.user_type.split(',')
            if 'VSA' in user_type:
                user_type.remove('VSA')
            self.user_type = ','.join(user_type)
        super(Teacher, self).save(*args, **kwargs)

    @property
    def nick_name(self):
        return '{}{}'.format(self.name, TEACHER_TYPE_MAP.get(self.teacher_type))

    @property
    def is_leader(self):
        return self.teacher_type == 'grade_director'

    @property
    def push_config(self):
        tags = [str(self.school.school_id).replace('-', '_')]
        tags.append(generate_md5(self.school.province))
        tags.append(generate_md5(self.school.city))
        tags.append(generate_md5(self.school.district))
        return {'alias': str(self.user_id).replace('-', '_'), 'tags': tags}

    def __str__(self):
        return self.nick_name

    class Meta:
        verbose_name = '教师'
        verbose_name_plural = verbose_name


class Student(models.Model):
    operator_code = models.CharField(default="", null=True, blank=True, max_length=16, verbose_name="运行商code")
    third_id = models.CharField(default="", max_length=16, verbose_name='THIRD_ID')
    student_id = models.CharField(default=get_unique_id, max_length=16, unique=True, verbose_name='ID')
    name = models.CharField(max_length=32, verbose_name='姓名')
    gender = models.CharField(max_length=1, choices=GENDER_CHOICE, verbose_name='性别')
    age = models.IntegerField(default=0, verbose_name='年龄')

    clazz = models.ForeignKey(to='school.Class', related_name='students', null=True, blank=True, verbose_name='班级')
    mobile = models.CharField(max_length=14, verbose_name='学生卡号码')

    def __str__(self):
        return self.name

    def get_attendance(self):
        pass

    class Meta:
        verbose_name = '学生'
        verbose_name_plural = verbose_name


class AuthToken(models.Model):
    key = models.CharField(max_length=40, verbose_name='KEY')
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, related_name='auth_token',
        on_delete=models.CASCADE, verbose_name="User"
    )
    created = models.DateTimeField(auto_now_add=True)
    expire = models.DateTimeField(verbose_name='过期时间')

    class Meta:
        verbose_name = "Token"
        verbose_name_plural = "Tokens"

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
            self.expire = now() + timedelta(days=2)
        return super(AuthToken, self).save(*args, **kwargs)

    def refresh_key(self):
        self.key = self.generate_key()
        self.expire = now() + timedelta(days=2)
        self.save()

    def generate_key(self):
        return binascii.hexlify(os.urandom(20)).decode()

    def __str__(self):
        return self.user.__str__()


fs = FileSystemStorage(location=settings.MEDIA_ROOT)
