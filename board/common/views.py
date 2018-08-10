# coding=utf-8

from rest_framework import exceptions
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.schemas import SchemaGenerator
from rest_framework.views import APIView
from common.renders import SwaggerRenderer


class SwaggerGenerator(SchemaGenerator):
    def has_view_permissions(self, path, method, view):
        return True


generator = SwaggerGenerator(title="Server API",
                             urlconf='StudentTrackingSystem.urls')


class SchemaView(APIView):
    _ignore_model_permissions = True
    exclude_from_schema = True
    renderer_classes = (SwaggerRenderer,)
    permission_classes = (permissions.AllowAny,)

    def get(self, request, *args, **kwargs):
        schema = generator.get_schema(request)
        if schema is None:
            raise exceptions.PermissionDenied()
        return Response(schema, headers={'Access-Control-Allow-Origin': '*'})
