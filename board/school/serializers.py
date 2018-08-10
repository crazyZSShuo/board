# coding=utf-8
import time
from rest_framework import serializers

from common.exception import APIError, errors
from school.defaults import TEACHER_ROLES
from school.models import School, Class, TeacherClassRelation
from user.models import Teacher, Student


class AjaxSchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = ('school_id', 'name', 'province', 'city', 'district', 'address')
        read_only_fields = fields


class AdminSchoolSerializer(serializers.ModelSerializer):
    principal_name = serializers.CharField(source="principal.name")
    logo = serializers.ImageField(required=False)
    admin_mobile = serializers.CharField(required=False)
    admin_password = serializers.CharField(required=False)

    def create(self, validated_data):
        try:
            admin = Teacher()
            admin.mobile = validated_data.pop('admin_mobile')
            admin.set_password(validated_data.pop('admin_password'))
            admin.name = '学校管理员'
            admin.user_type = 'T,SA'
            admin.save()
        except Exception as e:
            raise APIError(err_code=errors.ERROR_FAIL_TO_MODIFY_PARENT_MOBILE_DUPLICATE,
                           message='手机号码已存在')

        teacher = Teacher()
        teacher.teacher_type = "principal"
        teacher.name = validated_data['principal']['name']
        teacher.mobile = str(time.time())
        teacher.save()

        validated_data['principal'] = teacher
        instance = School.objects.create(**validated_data)
        teacher.school = instance
        teacher.save()
        admin.school = instance
        admin.save()

        return instance

    def update(self, instance, validated_data):
        if not instance.principal:
            principal = Teacher()
            principal.teacher_type = "principal"
            principal.mobile = str(time.time())
        else:
            principal = instance.principal
        principal.name = validated_data.pop("principal")['name']
        principal.save()
        return super().update(instance, validated_data)

    class Meta:
        model = School
        fields = ('school_id', 'name', 'province', 'city', 'district', 'address', 'logo', 'desc', 'principal_name',
                  'admin_mobile', 'admin_password')


class AdminTinySchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = ('school_id', 'name',)


class SchoolSerializer(serializers.ModelSerializer):
    principal = serializers.CharField(source='principal.name')
    logo = serializers.SerializerMethodField()
    logo_original = serializers.SerializerMethodField()

    def get_logo(self, obj):
        return '%s.s_logo_thumbnail' % obj.logo.url

    def get_logo_original(self, obj):
        return obj.logo.url

    class Meta:
        model = School
        fields = (
            'school_id', 'name', 'province', 'city', 'district', 'address', 'logo', 'logo_original', 'desc',
            'principal','news',)
        read_only_fields = fields


class ClassTeacherSerializer(serializers.ModelSerializer):
    nick_name = serializers.CharField(source='teacher.nick_name')
    mobile = serializers.CharField(source='teacher.mobile')
    avatar = serializers.ImageField(source='teacher.avatar')
    role = serializers.SerializerMethodField()

    def get_role(self, obj):
        return [x.name for x in obj.position.all()]

    class Meta:
        model = TeacherClassRelation
        fields = ('nick_name', 'mobile', 'role','avatar',)


class TinyClassSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='canonical_name')

    class Meta:
        model = Class
        fields = ('class_id', 'name')


class AdminClassSerializer(serializers.ModelSerializer):
    school = serializers.SlugRelatedField(slug_field='school_id', queryset=School.objects.all())
    school_province = serializers.CharField(read_only=True, source='school.province')
    school_city = serializers.CharField(read_only=True, source='school.city')
    school_district = serializers.CharField(read_only=True, source='school.district')
    school_name = serializers.CharField(read_only=True, source='school.name')
    canonical_name = serializers.CharField(read_only=True)

    def create(self, validated_data):
        try:
            Class.objects.get(start=validated_data['start'], index_of_grade=validated_data['index_of_grade'],
                              school=validated_data['school'])
            raise APIError(err_code=errors.SYSTEM_ERROR,
                           message='班级已存在')
        except Class.DoesNotExist as e:
            instance = super().create(validated_data)
            instance.grade_index = instance.current_grade_index
            instance.save()
            return instance

    class Meta:
        model = Class
        fields = ('class_id', 'index_of_grade', 'start', 'school', 'school_province', 'school_city',
                  'school_district', 'school_name', 'canonical_name', 'time_table')


class ClassSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='canonical_name')
    teacher = ClassTeacherSerializer(many=True, source='teacher_relations')
    role = serializers.SerializerMethodField()
    school = SchoolSerializer()

    def get_role(self, obj):
        if self.context['request'].user.is_teacher:
            try:
                rel = self.context['request'].user.teacher.class_relations.get(clazz=obj)
                return [TEACHER_ROLES[x] for x in rel.role]
            except TeacherClassRelation.DoesNotExist:
                pass

    class Meta:
        model = Class
        fields = (
            'class_id', 'name', 'desc','teacher', 'role', 'school')
        read_only_fields = (
            'class_id', 'name', 'desc', 'teacher', 'role', 'school')
