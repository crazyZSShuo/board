# coding=utf-8
import binascii

from django.contrib.auth import authenticate
from rest_framework import serializers

from common.exception import APIError
from school.defaults import TEACHER_ROLES
from school.models import Class, School, TeacherClassRelation
from school.serializers import SchoolSerializer, ClassSerializer
from user.models import UserProfile, Student, Teacher


class AuthTokenSerializer(serializers.Serializer):
    mobile = serializers.CharField(label="Mobile")
    password = serializers.CharField(label="Password", style={'input_type': 'password'})

    def validate(self, attrs):
        mobile = attrs.get('mobile')
        password = attrs.get('password')

        if mobile and password:
            user = authenticate(username=mobile, password=password)

            if user:
                # From Django 1.10 onwards the `authenticate` call simply
                # returns `None` for is_active=False users.
                # (Assuming the default `ModelBackend` authentication backend.)
                if not user.is_active:
                    msg = 'User account is disabled.'
                    raise serializers.ValidationError(msg, code='authorization')
            else:
                msg = 'Unable to log in with provided credentials.'
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = 'Must include "username" and "password".'
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs


class UserProfileSerializer(serializers.ModelSerializer):
    push_config = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()
    avatar_original = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        read_only_fields = ('mobile', 'user_type', 'avatar', 'avatar_original', 'push_config',)
        fields = (
            'mobile', 'nick_name', 'gender', 'birthday', 'address', 'user_type', 'avatar', 'avatar_original','push_config',)

    def get_avatar(self, obj):
        return '%s.avatar_thumbnail' % obj.avatar.url

    def get_avatar_original(self, obj):
        return obj.avatar.url


class TeacherProfileSerializer(UserProfileSerializer):
    class Meta(UserProfileSerializer.Meta):
        model = Teacher
        fields = (
            'mobile', 'nick_name', 'gender', 'birthday', 'address', 'user_type', 'avatar', 'avatar_original',
            'push_config','teacher_type')
        read_only_fields = ('mobile', 'user_type', 'avatar', 'avatar_original','push_config', 'teacher_type',)


class StudentSerializer(serializers.ModelSerializer):
    clazz = ClassSerializer()
    school = SchoolSerializer(source='clazz.school')
    mobile = serializers.CharField(source='device.mobile')

    class Meta:
        model = Student
        fields = ('student_id', 'name', 'gender', 'age', 'clazz', 'school', 'mobile',)
        read_only_fields = fields


import logging

logg = logging.getLogger("django")


class TinyStudentListSerializer(serializers.ModelSerializer):
    school_province = serializers.CharField(source='clazz.school.province')
    school_city = serializers.CharField(source='clazz.school.city')
    school_district = serializers.CharField(source='clazz.school.district')
    school_name = serializers.CharField(source='clazz.school.name')
    class_name = serializers.CharField(source='clazz.canonical_name')

    class Meta:
        model = Student
        fields = (
            'student_id', 'name', 'gender', 'age', 'school_province', 'school_city', 'school_district', 'school_name',
            'class_name')


class StudentListSerializer(serializers.ModelSerializer):
    clazz = serializers.CharField(source='clazz.canonical_name')
    school_province = serializers.CharField(source='clazz.school.province')
    school_city = serializers.CharField(source='clazz.school.city')
    school_district = serializers.CharField(source='clazz.school.district')
    school_name = serializers.CharField(source='clazz.school.name')

    class Meta:
        model = Student
        fields = ('student_id', 'name', 'gender', 'age', 'clazz', 'school_province', 'school_city',
                  'school_district', 'school_name')


class StudentDetailSerializer(serializers.ModelSerializer):
    school_province = serializers.CharField(source='clazz.school.province')
    school_city = serializers.CharField(source='clazz.school.city')
    school_district = serializers.CharField(source='clazz.school.district')
    school_name = serializers.CharField(source='clazz.school.name')
    school_id = serializers.CharField(source='clazz.school.school_id')

    clazz = serializers.CharField(source='clazz.canonical_name', read_only=True)
    class_id = serializers.SlugRelatedField(slug_field='class_id', source='clazz', queryset=Class.objects.all())
    age = serializers.IntegerField()

    class Meta:
        model = Student
        fields = (
            'school_id', 'school_province', 'school_city', 'school_district', 'school_name', 'student_id', 'name',
            'gender','age', 'clazz', 'class_id',)

    def create(self, validated_data):
        return super().create(validated_data)


class TeacherClassRelationSerializer(serializers.Serializer):
    clazz = serializers.CharField(source='clazz.canonical_name', read_only=True)
    class_id = serializers.SlugRelatedField(source='clazz', slug_field='class_id', queryset=Class.objects.all())
    role = serializers.ListField(child=serializers.IntegerField())
    role_desc = serializers.ListField(child=serializers.CharField(), read_only=True)

    def to_representation(self, instance):
        instance.role_desc = [TEACHER_ROLES[x] for x in instance.role]
        return super().to_representation(instance)


class TeacherDetailSerializer(serializers.Serializer):
    teacher_id = serializers.CharField(source='user_id', read_only=True)
    name = serializers.CharField()
    mobile = serializers.CharField()
    gender = serializers.CharField()
    school = serializers.CharField(source='school.name', read_only=True)
    school_id = serializers.SlugRelatedField(source='school', slug_field='school_id', queryset=School.objects.all())
    class_relations = TeacherClassRelationSerializer(many=True, required=False)

    def update(self, instance, validated_data):
        class_relations = validated_data.pop('class_relations')
        if class_relations:
            if instance.class_relations.all().count() > 0:
                instance.class_relations.all().delete()
            for rel in class_relations:
                tcr = TeacherClassRelation()
                tcr.teacher = instance
                tcr.clazz = rel['clazz']
                tcr.role = list(set(rel['role']))
                tcr.save()

        for attr, value in validated_data.items():
            if getattr(instance, attr) != value:
                setattr(instance, attr, value)
        instance.save()
        return instance

    def create(self, validated_data):
        try:
            class_relations = None
            if 'class_relations' in validated_data:
                class_relations = validated_data.pop('class_relations')
            instance = Teacher.objects.create(**validated_data)
            instance.set_password('123456')
            instance.save()
            if class_relations:
                for rel in class_relations:
                    tcr = TeacherClassRelation()
                    tcr.teacher = instance
                    tcr.clazz = rel['clazz']
                    tcr.role = list(set(rel['role']))
                    tcr.save()
            return instance
        except TypeError as e:
            print(e)
            raise APIError(err_code=999999, message='fail to create teacher')


class TeacherListSerializer(serializers.Serializer):
    teacher_id = serializers.CharField(source='user_id', read_only=True)
    name = serializers.CharField()
    mobile = serializers.CharField()
    gender = serializers.CharField()
    school = serializers.CharField(source='school.name', read_only=True)
    school_id = serializers.SlugRelatedField(source='school', slug_field='school_id', queryset=School.objects.all())


class AdminTeacherSerializer(serializers.ModelSerializer):
    school = serializers.SlugRelatedField(slug_field='school_id', queryset=School.objects.all())
    school_province = serializers.CharField(read_only=True, source='school.province')
    school_city = serializers.CharField(read_only=True, source='school.city')
    school_district = serializers.CharField(read_only=True, source='school.district')
    school_name = serializers.CharField(read_only=True, source='school.name')
    class_relations = TeacherClassRelationSerializer(many=True, required=False)
    mobile = serializers.CharField()
    is_leader = serializers.BooleanField()
    user_type = serializers.CharField(required=False)

    def create(self, validated_data):
        logg.info(validated_data)
        is_leader = validated_data.pop('is_leader')
        if is_leader:
            validated_data['teacher_type'] = 'grade_director'
        else:
            validated_data['teacher_type'] = 'teacher'

    def update(self, instance, validated_data):
        logg.info(validated_data)
        is_leader = validated_data.pop('is_leader')
        if is_leader:
            validated_data['teacher_type'] = 'grade_director'
        else:
            validated_data['teacher_type'] = 'teacher'

    class Meta:
        model = Teacher
        fields = (
            'user_id', 'user_type', 'school_province', 'school_city', 'school_district', 'school_name', 'school',
            'name','mobile', 'class_relations', 'is_leader')
