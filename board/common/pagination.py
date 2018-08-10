# coding=utf-8

from rest_framework import pagination


class LimitOffsetPagination(pagination.LimitOffsetPagination):
    limit_query_param = 'count'
    offset_query_param = 'start'


class ClassLimitOffsetPagination(LimitOffsetPagination):
    offset_query_param = 'class_start'
