from django.contrib import admin

# Register your models here.
from electronicboard.models import ClassGallery, GalleryImageItem, ClassNotification, ClassHonor, SchoolNews, Lesson, \
    TeacherExtraInfo, HonorImageItem,StudentLessonRel, LessonAttendanceHistory, LessonAttendanceStudent


class GalleryImageItemAdmin(admin.ModelAdmin):
    list_display = ('image', 'created_time',)


class ClassGalleryAdmin(admin.ModelAdmin):
    list_display = ('clazz', 'name', 'teacher', 'is_show', 'created_time',)


class ClassNotificationAdmin(admin.ModelAdmin):
    list_display = ('school', 'type', 'title', 'image', 'content', 'start', 'end', 'teacher', 'created_time',)


class ClassHonorAdmin(admin.ModelAdmin):
    list_display = ('class_honor_id', 'clazz', 'title', 'get_time', 'desc', 'teacher', 'created_time',)


class SchoolNewsAdmin(admin.ModelAdmin):
    list_display = ('school', 'title', 'picture', 'content', 'teacher', 'created_time',)


class LessonAdmin(admin.ModelAdmin):
    list_display = ('clazz', 'teacher', 'name', 'day_of_week', 'index_of_day', 'start', 'end', 'created_time',)


class TeacherExtraInfoAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'age', 'teacher_roles', 'work_years', 'graduate_school', 'achievement', 'introduce')


admin.site.register(GalleryImageItem)
admin.site.register(ClassGallery, ClassGalleryAdmin)
admin.site.register(ClassNotification, ClassNotificationAdmin)
admin.site.register(ClassHonor, ClassHonorAdmin)
admin.site.register(HonorImageItem)
admin.site.register(SchoolNews, SchoolNewsAdmin)
admin.site.register(Lesson, LessonAdmin)
admin.site.register(TeacherExtraInfo, TeacherExtraInfoAdmin)
admin.site.register(StudentLessonRel)
admin.site.register(LessonAttendanceHistory)
admin.site.register(LessonAttendanceStudent)
