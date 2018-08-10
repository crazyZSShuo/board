# coding=utf-8

from rest_framework import permissions
from school.models import School, Class
from user.models import Student, Teacher


class TeacherOnly(permissions.IsAuthenticated):
    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.is_teacher


class TeacherElectronicBoardOnly(permissions.IsAuthenticated):
    def has_permission(self, request, view):
        return super().has_permission(request, view) \
               and request.user.is_teacher \
               and hasattr(request.user, "teacher") \
               and hasattr(request.user.teacher, "extra_info") \
               and request.user.teacher.extra_info.clazz is not None


class SchoolAdminOnly(permissions.IsAuthenticated):
    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.is_school_admin


class SysAdminOnly(permissions.IsAuthenticated):
    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.is_system_admin


class AdminPermission(permissions.IsAuthenticated):

    def has_permission(self, request, view):
        return super().has_permission(request, view) and (
                    request.user.is_system_admin or request.user.is_school_admin or request.user.is_customer)

    def has_object_permission(self, request, view, obj):
        if request.user.is_system_admin:
            return True

        if request.user.is_customer and view.action in ["list", "retrieve"]:
            return True

        if isinstance(obj, School):
            return request.user.teacher.school == obj
        if isinstance(obj, Class):
            return request.user.teacher.school == obj.school
        if isinstance(obj, Student):
            return request.user.is_customer or request.user.teacher.school == obj.clazz.school
        if isinstance(obj, Teacher):
            return request.user.teacher.school == obj.school

        return super().has_object_permission(request, view, obj)
