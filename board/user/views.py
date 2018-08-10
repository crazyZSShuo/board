# coding=utf-8

import io
import logging
from copy import deepcopy

from django.contrib.auth import login as auth_login, logout as auth_logout
import django_filters
from rest_framework import mixins, filters
from rest_framework import permissions
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.views import APIView

from common import errors
from common.exception import APIError
from common.mixins import APIResponseMixin
from common.pagination import LimitOffsetPagination
from common.response import APIResponse
from school.defaults import TEACHER_ROLES
from school.models import School, Class
from school.serializers import ClassSerializer
from user.filters import StudentFilter, TeacherFilter
from user.models import UserProfile, AuthToken, Student, Teacher
from user.permissions import TeacherOnly, AdminPermission
from user.serializers import AuthTokenSerializer, UserProfileSerializer, StudentSerializer,  TeacherProfileSerializer, StudentListSerializer, \
    StudentDetailSerializer, \
    TeacherListSerializer, TeacherDetailSerializer, \
    AdminTeacherSerializer, TinyStudentListSerializer

logg = logging.getLogger("django")


class LoginView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = AuthTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = AuthToken.objects.get_or_create(user=user)
        if not created:
            token.refresh_key()

        try:
            school = None
            if user.is_teacher:
                teacher = Teacher.objects.get(pk=user.pk)
                school = teacher.school

            if hasattr(request.META, 'HTTP_X_FORWARDED_FOR'):
                ip = request.META['HTTP_X_FORWARDED_FOR']
            else:
                ip = request.META['REMOTE_ADDR']

        except Exception as e:
            logg.info(e)

        return APIResponse({'token': token.key, 'expire': token.expire})

    def perform_authentication(self, request):
        request._not_authenticated()
        return request.user


class WebLoginView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = AuthTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        auth_login(request, user)
        return APIResponse()


class WebLogoutView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        auth_logout(request)
        return APIResponse()


class UserProfileView(APIView):
    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.user)
        return APIResponse(serializer.data)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.update(self.user, validated_data=serializer.validated_data)
        return APIResponse(self.get_serializer(self.user).data)

    def check_permissions(self, request):
        # check super permission first
        super().check_permissions(request)
        # 临时修改
        if request.user.is_school_admin or request.user.is_system_admin or request.user.is_vice_school_admin or request.user.is_customer:
            self.user = self.request.user.teacher if hasattr(self.request.user,
                                                             'teacher') and self.request.query_params.get(
                'user_type') == 'teacher' else self.request.user
        else:
            if request.query_params.get('user_type') == 'teacher' and not request.user.is_teacher:
                raise APIError(err_code=errors.ERROR_NOT_A_TEACHER, message='You are not a teacher')

            self.user = self.request.user.teacher if self.request.query_params.get(
                'user_type') == 'teacher' else self.request.user

    @property
    def get_serializer(self, *args, **kwargs):
        return TeacherProfileSerializer if self.request.query_params.get(
            'user_type') == 'teacher' else UserProfileSerializer


class ClassView(viewsets.GenericViewSet, mixins.ListModelMixin, APIResponseMixin):
    serializer_class = ClassSerializer
    permission_classes = (TeacherOnly,)

    def get_queryset(self):
        teacher = self.request.user.teacher
        return teacher.classes.all()


class StudentView(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin, mixins.DestroyModelMixin,
                  mixins.UpdateModelMixin, mixins.RetrieveModelMixin, APIResponseMixin):
    pagination_class = LimitOffsetPagination
    lookup_field = 'student_id'
    filter_class = StudentFilter

    def get_queryset(self):
        return Student.objects.all()

    def remove_duplicate_item(self, instance, data, ddata=None):
        if not ddata:
            ddata = deepcopy(data)
        for k, v in data.items():
            if hasattr(instance, k):
                if isinstance(v, dict):
                    self.remove_duplicate_item(getattr(instance, k), v, ddata[k])
                if getattr(instance, k) == v:
                    ddata.pop(k)
        return ddata

    def update(self, request, *args, **kwargs):
        student = self.get_object()
        request._full_data = self.remove_duplicate_item(student, request.data)
        return super().update(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def get_serializer_class(self):
        if self.action in ['list']:
            return StudentListSerializer
        elif self.action in ['retrieve', 'partial_update', 'create', 'destroy']:
            return StudentDetailSerializer
        return super().get_serializer_class()


class TinyStudentListView(viewsets.GenericViewSet, mixins.ListModelMixin, APIResponseMixin):
    pagination_class = LimitOffsetPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    serializer_class = TinyStudentListSerializer
    permission_classes = [TeacherOnly]

    def get_queryset(self):
        teacher = self.request.user.teacher
        if teacher.school:
            return Student.objects.filter(clazz__school=teacher.school)
        else:
            return Student.objects.none()


class TeacherView(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin, mixins.RetrieveModelMixin,
                  mixins.DestroyModelMixin, mixins.UpdateModelMixin,
                  APIResponseMixin):
    queryset = Teacher.objects.all()
    pagination_class = LimitOffsetPagination
    lookup_field = 'user_id'

    def get_serializer_class(self):
        if self.action in ['list']:
            return TeacherListSerializer
        elif self.action in ['retrieve', 'destroy', 'update', 'partial_update', 'create']:
            return TeacherDetailSerializer
        return super().get_serializer_class()



class AdminTeacherView(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin,
                       mixins.RetrieveModelMixin, mixins.DestroyModelMixin, mixins.UpdateModelMixin,
                       APIResponseMixin):
    queryset = Teacher.objects.exclude(teacher_type='principal')
    pagination_class = LimitOffsetPagination
    lookup_field = 'user_id'
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend, filters.SearchFilter)
    serializer_class = AdminTeacherSerializer
    filter_class = TeacherFilter
    permission_classes = (AdminPermission,)
    search_fields = ('name', 'mobile')

    def get_queryset(self):
        query = super().get_queryset()
        if self.request.user.is_school_admin:
            return query.filter(school=self.request.user.teacher.school)
        return query

    def create(self, request, *args, **kwargs):
        if self.request.user.is_school_admin:
            request.data['school'] = self.request.user.teacher.school.school_id
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        if self.request.user.is_school_admin:
            request.data['school'] = self.request.user.teacher.school.school_id
        return super().update(request, *args, **kwargs)


@api_view(['GET'])
def teacher_role_list(request):
    result = []
    for index, r in enumerate(TEACHER_ROLES):
        if index == 0 or index == 9:
            result.append({'role': index, 'role_desc': r})
    return APIResponse(result)


from django.core.files.storage import FileSystemStorage
from django.conf import settings

fs = FileSystemStorage(location=settings.MEDIA_ROOT)
