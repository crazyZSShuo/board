from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Teacher, UserProfile, Student


class TeacherAdmin(admin.ModelAdmin):
    list_display = ('mobile', 'nick_name', 'gender', 'teacher_type', 'school')
    fields = (
    'user_id', 'mobile', 'name', 'nick_name', 'gender', 'avatar', 'birthday', 'address', 'desc', 'teacher_type','school',)
    readonly_fields = ('user_id', 'nick_name', 'nick_name',)


class UserProfileAdmin(UserAdmin):
    list_display = ('mobile', 'name', 'nick_name', 'gender', 'user_type', 'is_staff')
    fieldsets = (('ExtraInfo', {'fields': (
        'mobile', 'name', 'nick_name', 'gender', 'avatar', 'user_type', 'birthday',
        'address',)}),) + UserAdmin.fieldsets
    readonly_fields = ('nick_name',)
    search_fields = ('username', 'first_name', 'last_name', 'email', 'name', 'mobile')


class StudentAdmin(admin.ModelAdmin):
    fields = ('name', 'student_id', 'gender', 'age', 'clazz')
    readonly_fields = ('student_id',)
    list_display = ('name', 'student_id', 'clazz')
    search_fields = ('name',)


admin.site.register(Teacher, TeacherAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Student, StudentAdmin)
