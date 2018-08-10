import logging
from rest_framework import mixins, parsers
from rest_framework import viewsets
from rest_framework.decorators import detail_route

from common import errors
from common.mixins import APIResponseMixin
from common.pagination import LimitOffsetPagination, ClassLimitOffsetPagination
from common.response import APIResponse
from school.filters import SchoolFilter, ClassFilter
from school.models import School, Class
from school.serializers import SchoolSerializer, ClassSerializer, ClassTeacherSerializer, AdminSchoolSerializer, \
    AdminTinySchoolSerializer, AdminClassSerializer
from user.models import Student
from user.permissions import AdminPermission
from user.serializers import StudentSerializer

logger = logging.getLogger(__name__)


class SchoolView(viewsets.GenericViewSet, mixins.RetrieveModelMixin, APIResponseMixin):
    lookup_field = 'school_id'
    serializer_class = SchoolSerializer
    queryset = School.objects.all()
    pagination_class = LimitOffsetPagination


class AdminSchoolView(viewsets.GenericViewSet, mixins.RetrieveModelMixin, mixins.ListModelMixin,
                      mixins.UpdateModelMixin, mixins.CreateModelMixin, mixins.DestroyModelMixin,
                      APIResponseMixin):
    lookup_field = 'school_id'
    serializer_class = AdminSchoolSerializer
    queryset = School.objects.all()
    filter_class = SchoolFilter
    parser_classes = (parsers.MultiPartParser, parsers.JSONParser)
    pagination_class = LimitOffsetPagination

    def tiny_school(self, request, *args, **kwargs):
        if self.request.user.is_system_admin:
            queryset = self.filter_queryset(self.get_queryset())

            serializer = AdminTinySchoolSerializer(queryset, many=True)
            return APIResponse(data=serializer.data)
        return APIResponse(data=None)

    def list(self, request, *args, **kwargs):
        if self.request.user.is_school_admin or self.request.user.is_vice_school_admin or self.request.user.is_teacher:
            if self.request.user.teacher.school:
                return APIResponse(data=AdminSchoolSerializer(self.request.user.teacher.school).data)
            else:
                return APIResponse(code=errors.OTHER_ERROR, message="学校不存在")
        return super().list(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        if self.request.user.is_school_admin:
            if self.request.user.teacher.school:
                instance = self.request.user.teacher.school
                serializer = self.get_serializer(instance, data=request.data, partial=True)
                serializer.is_valid(raise_exception=True)
                self.perform_update(serializer)
                return APIResponse(data=serializer.data)
            else:
                return APIResponse(code=errors.OTHER_ERROR, message="学校不存在")
        return super().update(request, *args, **kwargs)


class ClassView(viewsets.GenericViewSet, mixins.RetrieveModelMixin, mixins.ListModelMixin, mixins.UpdateModelMixin,
                APIResponseMixin):
    lookup_field = 'class_id'
    serializer_class = ClassSerializer
    queryset = Class.objects.all()
    filter_fields = ('school__school_id',)
    pagination_class = LimitOffsetPagination

    @detail_route(methods=['GET'])
    def teacher(self, request, class_id):
        cls = self.get_object()
        serializer = ClassTeacherSerializer(cls.teacher_relations.all(), many=True)
        return APIResponse(serializer.data)


class AdminClassView(viewsets.GenericViewSet, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.ListModelMixin,
                     mixins.CreateModelMixin, mixins.DestroyModelMixin,
                     APIResponseMixin):
    lookup_field = 'class_id'
    serializer_class = AdminClassSerializer
    filter_class = ClassFilter
    pagination_class = ClassLimitOffsetPagination
    queryset = Class.objects.all()
    permission_classes = (AdminPermission,)

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


class StudentView(viewsets.GenericViewSet, mixins.RetrieveModelMixin, APIResponseMixin):
    lookup_field = 'student_id'
    serializer_class = StudentSerializer
    queryset = Student.objects.all()

    def get_object(self):
        return super().get_object()
