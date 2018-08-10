# coding=utf-8
import django_filters
from rest_framework import filters

from school.models import School, Class


class SchoolFilter(filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = School
        fields = ('province', 'city', 'district', 'name')


class ClassFilter(filters.FilterSet):
    school__name = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Class
        fields = ('school__school_id', 'school__province', 'school__city', 'school__district', 'school__name', 'start',
                  'index_of_grade')
