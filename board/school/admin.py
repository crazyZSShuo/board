from django.contrib import admin

from .models import School, Class, TeacherClassRelation, TeacherPosition


class SchoolAdmin(admin.ModelAdmin):
    fields = (
        'name', 'province', 'city', 'district', 'address', 'desc', 'logo', 'principal', 'create','update')
    readonly_fields = ('school_id', 'create', 'update')


class TeacherPositionAdmin(admin.ModelAdmin):
    fields = ('name', 'type')
    list_display = ('name', 'type')


class TeacherClassRelationAdmin(admin.ModelAdmin):
    fields = ('teacher', 'clazz', 'role')
    list_display = ('teacher', 'clazz')
    search_fields = ('teacher__name', 'teacher__mobile')


class TCRelationInline(admin.TabularInline):
    model = TeacherClassRelation


class ClassAdmin(admin.ModelAdmin):
    fields = ('name', 'canonical_name', 'class_id', 'index_of_grade', 'grade_index', 'base_index_of_grade', 'school',
              'desc','create', 'update', "start")
    readonly_fields = ('canonical_name', 'class_id', 'create', 'update')
    inlines = [TCRelationInline]
    list_display = ('canonical_name', 'class_id', 'school')


admin.site.register(School, SchoolAdmin)
admin.site.register(Class, ClassAdmin)
admin.site.register(TeacherClassRelation, TeacherClassRelationAdmin)
admin.site.register(TeacherPosition, TeacherPositionAdmin)
