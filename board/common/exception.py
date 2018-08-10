# coding=utf-8

import json

from django import http
from rest_framework import exceptions
from rest_framework.compat import set_rollback

from common.response import APIResponse
from . import errors


class APIError(Exception):
    def __init__(self, err_code, message='Internal Server Error'):
        self.err_code = err_code
        self.message = message

    def __unicode__(self):
        return u'[Error] %d: %s' % (self.err_code, self.message)


def exception_handler(exc, context):
    # Custom Error
    if isinstance(exc, APIError):
        set_rollback()
        return APIResponse(code=exc.err_code, message=exc.message, data=None)

    # Authentication
    if isinstance(exc, exceptions.AuthenticationFailed):
        return APIResponse(code=errors.TOKEN_EXPIRED, message=exc.default_detail, data={'detail': exc.detail},
                           status_code=exc.status_code)
    # Throttled
    if isinstance(exc, exceptions.Throttled):
        return APIResponse(code=errors.THROTTLE_REACHED, message=exc.default_detail, data={'detail': exc.detail})

    # Common
    if isinstance(exc, exceptions.APIException):
        # print(exc)
        return APIResponse(code=errors.OTHER_ERROR, message=exc.default_detail, data={'detail': exc.detail})


def server_error(request, template_name=None):
    ret = {
        'code': errors.SYSTEM_ERROR,
        'message': 'server error',
        'data': None
    }
    return http.HttpResponseServerError(json.dumps(ret), content_type='application/json')


def not_found_error(request, template_name=None):
    ret = {
        'code': errors.NOT_FOUND,
        'message': 'not found',
        'data': None
    }
    return http.HttpResponse(json.dumps(ret), content_type='application/json', status=404)
