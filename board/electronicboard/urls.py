from django.conf.urls import url
from rest_framework.routers import DefaultRouter

from electronicboard import views
from electronicboard.views import ClassInfoAPIView, LoginView, ClassIndexAPIView

router = DefaultRouter()

router.register(r'electronic_board/class_course_table', views.LessonFormViewSet, base_name='class_course_table')
router.register(r'electronic_board/class_notification', views.ClassNotificationViewSet, base_name='class_notification')
router.register(r'electronic_board/teacher', views.TeacherExtraInfoViewSet, base_name='teacher')
router.register(r'electronic_board/class_gallery', views.ClassGalleryViewSet, base_name='class_gallery')
router.register(r'electronic_board/class_honor', views.ClassHonorViewSet, base_name='class_honor')
router.register(r'electronic_board/school_news', views.SchoolNewsViewSet, base_name='school_news')

urlpatterns = [

    url(r'^electronic_board/login/$', LoginView.as_view(), name='login'),
    url(r'^electronic_board/class_info/$', ClassInfoAPIView.as_view(), name='electronic_board_class_info'),
    url(r'^electronic_board/index/$', ClassIndexAPIView.as_view(), name='electronic_board_index'),

]

urlpatterns += router.urls
