# coding=utf-8

SUCCESS = 0

SYSTEM_ERROR = 1
TOKEN_EXPIRED = 2
SMS_VERIFY_NO_MOBILE = 3
NOT_FOUND = 4
ERROR_THIRD_AUTHORIZE = 6000
ERROR_THIRD_ACCESS_TOKEN = 6001
ERROR_THIRD_CREATE_PARENT_ERROR = 6002
ERROR_THIRD_NONE_RFID = 6003
ERROR_THIRD_NONE_CHILD = 6004
THROTTLE_REACHED = 3001
PARAMETER_NOT_CORRECT = 6
# 设置关机模式失败
ERROR_FAIL_POWER_OFF = 2001
# 打开假日模式失败
ERROR_ENABLE_HOLIDAY_MODE = 2002
# 关闭假日模式失败
ERROR_DISABLE_HOLIDAY_MODE = 2002

# 不是教师
ERROR_NOT_A_TEACHER = 4001
# 不是家长
ERROR_NOT_A_PARENT = 4002
# 不是管理员
ERROR_NOT_A_ADMIN = 4003

# 创建家长失败:电话号码已存在
ERROR_FAIL_TO_CREATE_PARENT_ALREADY_EXIST = 41001
# 创建家长失败:未知
ERROR_FAIL_TO_CREATE_PARENT_UNKNOWN = 41002
# 修改家长失败:电话号码已存在
ERROR_FAIL_TO_MODIFY_PARENT_MOBILE_DUPLICATE = 41003
# 创建家长失败:缺少参数
ERROR_FAIL_TO_CREATE_PARENT_PARAMETER_MISSING = 41004
# 修改家长失败:缺少 relation
ERROR_FAIL_TO_MODIFY_PARENT_RELATION_MISSING = 41005

OTHER_ERROR = 99

ERROR_NOT_ENROLLING_TIME = 50001
ERROR_ENROLL_FAILED_ABORTED = 50002
ERROR_ENROLL_FAILED_ALREADY_ENROLLED = 50003
ERROR_FAILED_UNENROLLED_COURSE = 50004
ERROR_FAILED_DATA_ERROR = 50005
ERROR_FAILED_NOT_ENROLLED = 50006
ERROR_FAILED_CANCEL_ADMITTED_COURSE = 50007
ERROR_FAILED_ADMIT_NOT_ENROLLED = 50008
ERROR_FAILED_ADMIT_CANCEL_NOT_ADMITTED = 50009

ERROR_EXT_COURSE_ALREADY_CHECKED_IN = 51001
ERROR_EXT_COURSE_NOT_IN_ENROLL_STATUS = 51002
ERROR_EXT_COURSE_NOT_IN_ENROLL_FINISHED_STATUS = 51003
ERROR_EXT_COURSE_NOT_IN_CLASS_STATUS = 51004

ERROR_FAILED_TO_INVITE = 52001
ERROR_FAILED_TO_ADMIT = 52002
ERROR_FAILED_TO_ADMIT_CANCEL = 52003
ERROR_FAILED_TO_ENROLL = 52004
ERROR_FAILED_TO_ENROLL_CANCEL = 52005
ERROR_FAILED_TO_ACCEPT_INVITE = 52006
ERROR_FAILED_TO_REJECT_INVITE = 52007
ERROR_FAILED_TO_ENROLL_ALREADY_INVITED = 52008
ERROR_FAILED_TO_ENROLL_NUMBER_FULL = 52009
ERROR_FAILED_TO_ENROLL_NOT_IN_TIME = 52010

ERROR_XLS_PARSE_ERROR = 53001
ERROR_TEST_RESULT_PUBLISH_PARSED_ERROR = 53002
ERROR_TEST_RESULT_PUBLISH_ALREADY_PUBLISHED = 53003

ERROR_SCHOOL_ADMIN_SET_EXCEED_MAX = 54001
ERROR_SCHOOL_ADMIN_TEACHER_NOT_EXIST = 54002

ERROR_EXT_COURSE_LIKE_ALREADY_LIKED = 55001
