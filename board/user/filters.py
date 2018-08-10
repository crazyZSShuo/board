# coding=utf-8

from rest_framework import filters

import django_filters

from user.models import Student, Teacher


class StudentFilter(filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    clazz__school__name = django_filters.CharFilter(lookup_expr='icontains')
    parents__name = django_filters.CharFilter(lookup_expr='icontains')

    # def filter_clazz__start(self, queryset, name, value):
    #     print(value)
    #     return queryset
    #
    # grade = django_filters.DateFilter(name="clazz__start", method=filter_clazz__start)

    # grade = django_filters.CharFilter(name="clazz__start", method='filter_grade')
    #
    # def filter_grade(self, queryset, name, value):
    #     return queryset;

    class Meta:
        model = Student
        fields = ('parents__name', 'clazz__school__province','clazz__school__city','clazz__school__district','clazz__school__name','clazz__start','clazz__index_of_grade','name',)


class TeacherFilter(filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    school__name = django_filters.CharFilter(lookup_expr='icontains')
    is_leader = django_filters.CharFilter(name="teacher_type", method='filter_leader')

    def filter_leader(self, queryset, name, value):
        if value == 'true':
            return queryset.filter(teacher_type='grade_director')
        return queryset

    class Meta:
        model = Teacher
        fields = ('school__province', 'school__city', 'school__district', 'school__name', 'name', 'is_leader')
