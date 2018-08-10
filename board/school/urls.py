# coding=utf-8

from django.conf.urls import url
from rest_framework import routers
from school.views import SchoolView, ClassView, AdminClassView, AdminSchoolView

urlpatterns = [
    url(r'^class/(?P<class_id>[^/.]+)/$', ClassView.as_view(actions={'get': 'retrieve', 'post': 'partial_update'})),
    url(r'^admin/tiny_school/$', AdminSchoolView.as_view(actions={'get': 'tiny_school', })),
]

router = routers.SimpleRouter()

router.register('school', SchoolView, 'school')
router.register('class', ClassView, 'class')

router.register('admin/school', AdminSchoolView, 'admin_school')
router.register('admin/class', AdminClassView, 'admin_class')

urlpatterns += router.urls
