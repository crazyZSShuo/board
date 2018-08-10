# coding=utf-8

from rest_framework import status
from rest_framework.response import Response
from collections import OrderedDict

from . import errors


class APIResponse(Response):
    def __init__(self, data=None, code=errors.SUCCESS, message=None, status_code=status.HTTP_200_OK):
        if code == errors.SUCCESS and not message:
            message = 'success'

        if code != errors.SUCCESS:
            status_code = status.HTTP_400_BAD_REQUEST

        if isinstance(data, dict) and 'count' in data.keys():
            ret = OrderedDict([
                ('code', code),
                ('message', message),
                ('paginated', True),
                ('total', data['count']),
                ('data', data['results'])
            ])
        else:
            ret = OrderedDict([
                ('code', code),
                ('message', message),
                ('data', data)
            ])

        super(APIResponse, self).__init__(ret, status=status_code)
