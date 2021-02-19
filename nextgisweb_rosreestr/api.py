# -*- coding: utf-8 -*-
from __future__ import division, absolute_import, print_function, unicode_literals
from collections import namedtuple

from nextgisweb.env import env
from nextgisweb.models import DBSession
from nextgisweb.feature_layer import IFeatureLayer, IWritableFeatureLayer
from nextgisweb.feature_layer.api import deserialize
from nextgisweb.resource import DataScope, resource_factory, Resource
from rrd_utils.utils import rrd_file_iterator_with_origin_name

PERM_WRITE = DataScope.write

ImportParams = namedtuple('ImportParams', [
    'file_upload_id',
    'update_exist_resources',
    'search_field'
])

CadastralResources = namedtuple('ImportResource', [
    'parcel_resource_id',
    'oks_polygon_resource_id',
    'oks_linear_resource_id',
    'oks_point_resource_id',
    'bound_resource_id',
    'oms_resource_id',
    'zone_resource_id',
])


def rosreestr_import(request):
    request.resource_permission(PERM_WRITE)

    data = ImportParams(**request.json_body)
    resources = CadastralResources(**request.json_body)


def setup_pyramid(comp, config):
    config.add_route(
        'rosreestr.import', '/api/resource/{id}/feature/import', factory=resource_factory
    ) \
        .add_view(rosreestr_import, route_name='rosreestr.export', context=Resource, request_method='POST')
