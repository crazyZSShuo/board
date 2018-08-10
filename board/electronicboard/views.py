from rest_framework.views import APIView
from rest_framework.pagination import LimitOffsetPagination
from rest_framework import mixins, viewsets, decorators, permissions
from rest_framework.views import APIView

from common.mixins import APIResponseMixin, APIResponse

from django.db.models import Q

from electronicboard.models import GalleryImageItem, ClassGallery, ClassNotification, ClassHonor, SchoolNews, Lesson, \
    TeacherExtraInfo, LessonAttendanceStudent
from electronicboard.serializers import ClassNotificationSerializer, \
    ClassHonorSerializer, SchoolNewsSerializer, LessonSerializer, TeacherExtraInfoSerializer, \
    ClassInfoSerializer, TeacherExtraInfoDetailSerializer, GalleryImageItemSerializer, \
    ClassHonorDetailSerializer, ClassGallerySerializer, ClassIndexSerializer, LessonAttendanceSerializer, \
    UUIDSerializer, HistoryAttendanceQuerySerializer, LessonAttendanceHistoryItemSerializer

from user.models import AuthToken
from user.permissions import TeacherElectronicBoardOnly


class LoginView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = UUIDSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = AuthToken.objects.get_or_create(user=user)

        if not created:
            token.refresh_key()
        return APIResponse({'token': token.key, 'expire': token.expire})

    def perform_authentication(self, request):
        request._not_authenticated()
        return request.user


class ClassInfoAPIView(APIView):
    permission_classes = (TeacherElectronicBoardOnly,)

    def get(self, request):
        return APIResponse(data=ClassInfoSerializer(instance=request.user.teacher.extra_info.clazz).data)


class ClassIndexAPIView(APIView):
    permission_classes = (TeacherElectronicBoardOnly,)

    def get(self, request):
        notification = ClassNotification.objects.filter(
            Q(school=self.request.user.teacher.school) |
            Q(clazz=self.request.user.teacher.extra_info.clazz)).first()
        honor = ClassHonor.objects.filter(Q(clazz=self.request.user.teacher.extra_info.clazz)).first()
        news = SchoolNews.objects.filter(Q(school=self.request.user.teacher.school)).first()

        return APIResponse(data=ClassIndexSerializer({
            'notification': notification,
            'honor': honor,
            'news': news,
        }).data)


class LessonFormViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, APIResponseMixin):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = (TeacherElectronicBoardOnly,)
    pagination_class = LimitOffsetPagination
    lookup_field = 'lesson_id'

    def get_serializer_class(self):
        if self.action == 'upload_attendances':
            return LessonAttendanceSerializer

        return super().get_serializer_class()

    def get_queryset(self):
        q = Q(clazz=self.request.user.teacher.extra_info.clazz)
        return Lesson.objects.filter(q).order_by('-created_time').all()

    @decorators.detail_route(methods=['POST', ], )
    def upload_attendances(self, request, lesson_id):
        return APIResponse()

    @decorators.detail_route(methods=['GET', ], )
    def history_attendances(self, request, lesson_id):
        serializer = HistoryAttendanceQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        date = serializer.validated_data['date']
        items = LessonAttendanceStudent.objects.filter(history__date=date, history__lesson=self.get_object())
        return APIResponse(data=LessonAttendanceHistoryItemSerializer(instance=items, many=True).data)


class ClassNotificationViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, APIResponseMixin):
    permission_classes = (TeacherElectronicBoardOnly,)
    serializer_class = ClassNotificationSerializer
    pagination_class = LimitOffsetPagination
    filter_fields = ('type',)

    def get_queryset(self):
        q = Q(school=self.request.user.teacher.school) | Q(clazz=self.request.user.teacher.extra_info.clazz)
        return ClassNotification.objects.filter(q).order_by('-created_time').all()


class TeacherExtraInfoViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin,
                              APIResponseMixin):
    permission_classes = (TeacherElectronicBoardOnly,)
    serializer_class = TeacherExtraInfoSerializer
    pagination_class = LimitOffsetPagination
    lookup_field = 'extra_info_id'

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return TeacherExtraInfoDetailSerializer

        return super().get_serializer_class()

    def get_queryset(self):
        q = Q(teacher__school=self.request.user.teacher.school) | Q(clazz=None)
        return TeacherExtraInfo.objects.filter(q).all()


class ClassGalleryViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin, APIResponseMixin):
    queryset = ClassGallery.objects.all()
    serializer_class = ClassGallerySerializer
    permission_classes = (TeacherElectronicBoardOnly,)

    @decorators.list_route(methods=['GET', ], )
    def imgs(self, request):
        data = GalleryImageItem.objects.filter(

            gallery__clazz=request.user.teacher.extra_info.clazz,
            gallery__is_show=True
        ).all()
        return APIResponse(data=GalleryImageItemSerializer(instance=data, many=True).data)


class ClassHonorViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin, APIResponseMixin):
    serializer_class = ClassHonorSerializer
    permission_classes = (TeacherElectronicBoardOnly,)
    pagination_class = LimitOffsetPagination
    lookup_field = 'class_honor_id'

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ClassHonorDetailSerializer

        return super().get_serializer_class

    def get_queryset(self):
        q = Q(clazz=self.request.user.teacher.extra_info.clazz)
        return ClassHonor.objects.filter(q).order_by('-created_time')


class SchoolNewsViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, APIResponseMixin):
    serializer_class = SchoolNewsSerializer
    permission_class = (TeacherElectronicBoardOnly,)
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        q = Q(school=self.request.user.teacher.school)
        return SchoolNews.objects.filter(q).order_by('-created_time')
