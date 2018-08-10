from datetime import timedelta, datetime

from rest_framework import serializers

from electronicboard.models import GalleryImageItem, ClassNotification, ClassHonor, SchoolNews, Lesson, \
    TeacherExtraInfo, \
    HonorImageItem, ClassGallery, LessonAttendanceHistory, LessonAttendanceStudent
from school.models import Class
from user.models import Student, Teacher


class UUIDSerializer(serializers.Serializer):
    uuid = serializers.CharField()

    def validate(self, attrs):
        uuid = attrs.get('uuid')
        try:
            user = Teacher.objects.get(mobile=13800138000)
            if not user.is_active:
                msg = 'User account is disabled.'
                raise serializers.ValidationError(msg, code='authorization')
            attrs['user'] = user
            return attrs

        except:
            msg = 'Unable to log in with provided credentials.'
            raise serializers.ValidationError(msg, code='authorization')


class ClassInfoSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    address = serializers.SerializerMethodField()
    bg = serializers.SerializerMethodField()
    city_number = serializers.SerializerMethodField()

    def get_name(self, obj):
        return obj.new_canonical_name

    def get_address(self, obj):
        return obj.school.address

    def get_bg(self, obj):
        return ''

    def get_city_number(self, obj):
        return '1010010'

    class Meta:
        model = Class
        fields = ('class_id', 'address', 'name', 'bg', 'city_number')


class LessonStudentSerializer(serializers.ModelSerializer):
    device_id = serializers.CharField(source='device.device_id')
    original_class = serializers.CharField(source='clazz.new_canonical_name')

    class Meta:
        model = Student
        fields = ('student_id', 'device_id', 'original_class', 'name')


class LessonSerializer(serializers.ModelSerializer):
    teacher = serializers.CharField(source='teacher.name')
    teacher_id = serializers.CharField(source='teacher.user_id')
    teacher_portrait = serializers.CharField(source='teacher.avatar')
    students = LessonStudentSerializer(many=True)
    start_attendance_time = serializers.SerializerMethodField()

    def get_start_attendance_time(self, obj):
        return (datetime.combine(datetime.now().date(), obj.start) - timedelta(minutes=10)).time()

    class Meta:
        model = Lesson
        fields = (
            'lesson_id', 'teacher_id', 'teacher_portrait', 'students', 'name', 'teacher', 'start', 'end', 'day_of_week', \
            'index_of_day', 'start_attendance_time', 'is_attendance')


class LessonAttendanceSerializer(serializers.Serializer):
    student = serializers.SlugRelatedField(slug_field='student_id', queryset=Student.objects.all())
    attendance = serializers.DateTimeField()


class HistoryAttendanceQuerySerializer(serializers.Serializer):
    date = serializers.DateField()


class LessonAttendanceHistoryItemSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.name')
    student_original_class = serializers.CharField(source='student.clazz.new_canonical_name')

    class Meta:
        model = LessonAttendanceStudent
        fields = ('student_name', 'student_original_class', 'attendance_time')


class ClassNotificationSerializer(serializers.ModelSerializer):
    from_name = serializers.CharField(source='teacher.name')
    inscription = serializers.SerializerMethodField()

    def get_inscription(self, obj):
        return '教务处'

    class Meta:
        model = ClassNotification
        fields = ('title', 'content', 'image', 'created_time', 'type', 'from_name', 'inscription')


class TeacherExtraInfoSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='teacher.name')
    portrait = serializers.CharField(source='teacher.avatar')
    teacher_id = serializers.CharField(source='extra_info_id')

    class Meta:
        model = TeacherExtraInfo
        fields = ('teacher_id', 'portrait', 'teacher_roles', 'name', 'age', 'work_years')


class TeacherExtraInfoDetailSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='teacher.name')
    portrait = serializers.CharField(source='teacher.avatar')
    teacher_id = serializers.CharField(source='extra_info_id')

    class Meta:
        model = TeacherExtraInfo
        fields = ('teacher_id', 'teacher_roles', 'name', 'age', 'work_years', 'graduate_school', 'achievement', \
                  'introduce', 'portrait')


class ClassGallerySerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassGallery
        fields = '__all__'


class GalleryImageItemSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source='gallery.title')

    class Meta:
        model = GalleryImageItem
        fields = ('image', 'title')


class ClassHonorSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassHonor
        fields = ('class_honor_id', 'get_time', 'title')


class HonorImageItemSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source='honor.title')

    class Meta:
        model = HonorImageItem
        fields = ('image', 'title')


class ClassHonorDetailSerializer(serializers.ModelSerializer):
    images = HonorImageItemSerializer(many=True)

    class Meta:
        model = ClassHonor
        fields = ('class_honor_id', 'get_time', 'title', 'images')


class SchoolNewsSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    def get_url(self, obj):
        return ''

    class Meta:
        model = SchoolNews
        fields = ('title', 'url', 'created_time')


class ClassIndexSerializer(serializers.Serializer):
    honor = ClassHonorSerializer()
    notification = ClassNotificationSerializer()
    news = SchoolNewsSerializer()
