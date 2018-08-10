# coding=utf-8

from .response import APIResponse


def deco(func):
    def new_func(*args, **kwargs):
        ret = func(*args, **kwargs)
        if isinstance(ret, APIResponse):
            return ret
        return APIResponse(ret.data)

    return new_func


class APIResponseMixin(object):
    def __getattribute__(self, *args, **kwargs):
        ret = super().__getattribute__(*args, **kwargs)
        actions = ['create', 'list', 'retrieve', 'update', 'partial_update', 'destroy']
        if args[0] in actions:
            ret = deco(ret)
        return ret
