# -*- coding: utf-8 -*-
from __future__ import division, absolute_import, print_function, unicode_literals
from json import dumps

from pyramid.response import Response
from nextgisweb.env import env
from nextgisweb.feature_layer import IFeatureLayer
from nextgisweb.resource import DataScope, DataStructureScope, resource_factory, Resource

from .util import find_bind_attribure


def bind_get(resource, request):
    request.resource_permission(DataStructureScope.read)

    bind_attribute = find_bind_attribure(resource)
    if bind_attribute is None:
        return Response(status=404)
    else:
        return Response(
            dumps(bind_attribute),
            content_type='application/json',
            charset='utf-8'
        )


def setup_pyramid(comp, config):
    config.add_route(
        'feature_layer.inspect', '/api/resource/{id}/bind', factory=resource_factory) \
        .add_view(bind_get, context=IFeatureLayer, request_method='GET')
