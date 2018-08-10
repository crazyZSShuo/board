# coding=utf-8

from django.conf.urls import url
from rest_framework import routers

from .views import LoginView, UserProfileView, ClassView, StudentView, \
    TeacherView, teacher_role_list, AdminTeacherView, TinyStudentListView, WebLoginView, WebLogoutView

router = routers.SimpleRouter()
# router.register('user/message', UserMessageView, base_name='message')
router.register('user/class', ClassView, base_name='class')
router.register('admin/teacher', AdminTeacherView, base_name='admin_teacher')

urlpatterns = [
    url(r'^user/login/$', LoginView.as_view(), name='login'),
    url(r'^user/web_login/$', WebLoginView.as_view(), name='web_login'),
    url(r'^user/web_logout/$', WebLogoutView.as_view(), name='web_logout'),
    url(r'^user/profile/$', UserProfileView.as_view(), name='profile'),
    url(r'^student/$', StudentView.as_view(actions={'get': 'list', 'post': 'create'})),
    url(r'^ext_course_teacher/student/$', TinyStudentListView.as_view(actions={'get': 'list'})),
    url(r'^student/(?P<student_id>[^/.]+)/$',
        StudentView.as_view(actions={'get': 'retrieve', 'post': 'partial_update', 'delete': 'destroy'})),
    # Teacher
    url(r'^teacher/$', TeacherView.as_view(actions={'get': 'list', 'post': 'create'})),
    url(r'^teacher/role/$', teacher_role_list),
    url(r'^teacher/(?P<user_id>[^/.]+)/$',
        TeacherView.as_view(actions={'get': 'retrieve', 'post': 'partial_update', 'delete': 'destroy'})),
]

urlpatterns += router.urls
