# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals
import zipfile
import shapely

from collections import namedtuple

from nextgisweb import db
from nextgisweb.env import env
from nextgisweb.feature_layer import Feature, IWritableFeatureLayer
from nextgisweb.feature_layer.api import deserialize as rr2ngw
from nextgisweb.geojson import dumps
from nextgisweb.lib.geometry import Geometry, Transformer
from nextgisweb.models import declarative_base
from nextgisweb.resource import (
    Permission,
    Resource,
    ResourceGroup,
    ResourceScope,
    Scope,
    Serializer,
    SerializedProperty as SP,
    SerializedResourceRelationship as SRR
)
from nextgisweb.resource.exception import ResourceError, ValidationError
from nextgisweb.spatial_ref_sys import SRS
from rrd_utils.utils import rrd_file_iterator
from rrd_xml_parser.parser import ParserXML
from six import ensure_str

from .util import _, COMP_ID, find_bind_attribure

Base = declarative_base()


class RosreestrScope(Scope):
    identity = COMP_ID
    label = _("Rosreestr")

    write = Permission(_("Write"))
    read = Permission(_("Read"))


class Rosreestr(Resource):
    identity = COMP_ID
    cls_display_name = _("Rosreestr")

    __scope__ = RosreestrScope

    parcel_resource_id = db.Column(db.ForeignKey(Resource.id), nullable=True)
    oks_polygon_resource_id = db.Column(db.ForeignKey(Resource.id), nullable=True)
    oks_linear_resource_id = db.Column(db.ForeignKey(Resource.id), nullable=True)
    oks_point_resource_id = db.Column(db.ForeignKey(Resource.id), nullable=True)
    spatial_data_resource_id = db.Column(db.ForeignKey(Resource.id), nullable=True)
    bound_resource_id = db.Column(db.ForeignKey(Resource.id), nullable=True)
    bound_linear_resource_id = db.Column(db.ForeignKey(Resource.id), nullable=True)
    oms_resource_id = db.Column(db.ForeignKey(Resource.id), nullable=True)
    zone_resource_id = db.Column(db.ForeignKey(Resource.id), nullable=True)

    parcel_resource = db.relationship(Resource, foreign_keys=parcel_resource_id)
    oks_polygon_resource = db.relationship(Resource, foreign_keys=oks_polygon_resource_id)
    oks_linear_resource = db.relationship(Resource, foreign_keys=oks_linear_resource_id)
    oks_point_resource = db.relationship(Resource, foreign_keys=oks_point_resource_id)
    spatial_data_resource = db.relationship(Resource, foreign_keys=spatial_data_resource_id)
    bound_resource = db.relationship(Resource, foreign_keys=bound_resource_id)
    bound_linear_resource = db.relationship(Resource, foreign_keys=bound_resource_id)
    oms_resource = db.relationship(Resource, foreign_keys=oms_resource_id)
    zone_resource = db.relationship(Resource, foreign_keys=zone_resource_id)

    @classmethod
    def check_parent(cls, parent):
        return (parent is None) or isinstance(parent, ResourceGroup)

    @classmethod
    def only_child(cls, parent):
        return all([not isinstance(child, cls) for child in parent.children])


PR_READ = ResourceScope.read
PR_UPDATE = ResourceScope.update

_mdargs = dict(read=PR_READ, write=PR_UPDATE)

_rrargs = dict(read=RosreestrScope.read, write=RosreestrScope.write)


class _source_attr(SP):

    def setter(self, srlzr, value):
        datafile, metafile = env.file_upload.get_filename(value['id'])

        if not zipfile.is_zipfile(datafile):
            ResourceError(_('Document should be in ZIP-file'))


class _update_attr(SP):

    def setter(self, srlzr, value):
        srlzr.obj.update = value

    def getter(self, srlzr):
        return srlzr.obj.id is not None


class BindAttributeSerializer(SP):

    def __init__(self, res_name, *args, **kwargs):
        super(BindAttributeSerializer, self).__init__(*args, **kwargs)
        self._resource_name = res_name

    def getter(self, srlzr):
        _bind_attr = find_bind_attribure(getattr(srlzr.obj, self._resource_name, None))
        if _bind_attr is None:
            return
        else:
            return dumps(_bind_attr)

    def setter(self, srlzr, value):
        res = getattr(srlzr.obj, self._resource_name, None)
        if res is None:
            return

        if not IWritableFeatureLayer.providedBy(res):
            ValidationError(_("Resource {} is not writable.".format(res.keyname)))

        if value not in {field.keyname for field in res.fields}:
            raise ValidationError(_("Attribute {} is not allowed".format(value)))


ResourceType = namedtuple('TResourceType', [
    'parcel_resource',
    'oks_polygon_resource',
    'oks_linear_resource',
    'oks_point_resource',
    'spatial_data_resource',
    'bound_resource',
    'bound_linear_resource',
    'oms_resource',
    'zone_resource'
    ])

ResourceAttrType = namedtuple('TResourceAttrType', [
    'parcel_bind_attr',
    'oks_polygon_bind_attr',
    'oks_linear_bind_attr',
    'oks_point_bind_attr',
    'spatial_data_bind_attr',
    'bound_bind_attr',
    'bound_linear_bind_attr',
    'oms_bind_attr',
    'zone_bind_attr'
    ])

ResourceByFeature = {
    ('Parcel', 'Polygon'): dict(
        resource='parcel_resource',
        bind='parcel_bind_attr',
    ),
    ('Building', 'Polygon'): dict(
        resource='oks_polygon_resource',
        bind='oks_polygon_bind_attr'
    ),
    ('Construction', 'Polygon'): dict(
        resource='oks_polygon_resource',
        bind='oks_polygon_bind_attr'
    ),
    ('Construction', 'LineString'): dict(
        resource='oks_linear_resource',
        bind='oks_linear_bind_attr'
    ),
    ('Construction', 'Point'): dict(
        resource='oks_point_resource',
        bind='oks_point_bind_attr'
    ),
    ('Uncompleted', 'Polygon'): dict(
        resource='oks_polygon_resource',
        bind='oks_polygon_bind_attr'
    ),
    ('Uncompleted', 'LineString'): dict(
        resource='oks_linear_resource',
        bind='oks_linear_bind_attr'
    ),
    ('Uncompleted', 'Point'): dict(
        resource='oks_point_resource',
        bind='oks_point_bind_attr'
    ),
    ('SpatialData', 'Polygon'): dict(
        resource='spatial_data_resource',
        bind='spatial_data_bind_attr'
    ),
    ('Bound', 'Polygon'): dict(
        resource='bound_resource',
        bind='bound_bind_attr'
    ),
    ('Bound', 'LineString'): dict(
        resource='bound_linear_resource',
        bind='bound_linear_bind_attr'
    ),
    ('OMSPoint', 'Point'): dict(
        resource='oms_resource',
        bind='oms_bind_attr'
    ),
    ('Zone', 'Polygon'): dict(
        resource='zone_resource',
        bind='zone_bind_attr'
    )
}


class RosreestrSerializer(Serializer):

    identity = Rosreestr.identity
    resclass = Rosreestr

    parcel_resource = SRR(**_mdargs)
    oks_polygon_resource = SRR(**_mdargs)
    oks_linear_resource = SRR(**_mdargs)
    oks_point_resource = SRR(**_mdargs)
    spatial_data_resource = SRR(**_mdargs)
    bound_resource = SRR(**_mdargs)
    bound_linear_resource = SRR(**_mdargs)
    oms_resource = SRR(**_mdargs)
    zone_resource = SRR(**_mdargs)

    source = _source_attr(read=None, write=RosreestrScope.write)
    update = _update_attr(read=RosreestrScope.read, write=RosreestrScope.write)

    parcel_bind_attr = BindAttributeSerializer('parcel_resource', **_rrargs)
    oks_polygon_bind_attr = BindAttributeSerializer('oks_polygon_resource', **_rrargs)
    oks_linear_bind_attr = BindAttributeSerializer('oks_linear_resource', **_rrargs)
    oks_point_bind_attr = BindAttributeSerializer('oks_point_resource', **_rrargs)
    spatial_data_bind_attr = BindAttributeSerializer('spatial_data_resource', **_rrargs)
    bound_bind_attr = BindAttributeSerializer('bound_resource', **_rrargs)
    bound_linear_bind_attr = BindAttributeSerializer('bound_linear_resource', **_rrargs)
    oms_bind_attr = BindAttributeSerializer('oms_resource', **_rrargs)
    zone_bind_attr = BindAttributeSerializer('zone_resource', **_rrargs)

    def deserialize(self):
        super(RosreestrSerializer, self).deserialize()
        comp = env.rosreestr

        updated = self.data.get('update')
        datafile, metafile = env.file_upload.get_filename(self.data['source']['id'])
        srs = self.data['srs']
        if srs is not None:
            srs_from = SRS.filter_by(id=int(srs)).one()
        else:
            srs_from = SRS.filter_by(id=3857).one()
        transformers = dict()

        # NOTE: Эта строка для отключения ускорения т.к. на Windows появляется ошибка при создании геометрии
        shapely.speedups.disable()
        for xml_file in rrd_file_iterator(datafile):
            parser = ParserXML()
            for rrfeature in parser.parse(xml_file):
                comp.logger.debug('Type: %s, Number: %s', rrfeature.type, rrfeature.registration_number)
                if rrfeature.geometry is None:
                    continue

                feature_geometry = Geometry.from_wkt(rrfeature.geometry, srid=srs_from.id)
                geometry_type = feature_geometry.shape.type
                if geometry_type.startswith('Multi'):
                    geometry_type = geometry_type[5:]

                feature_type = rrfeature.type
                if feature_type.startswith('Sub'):
                    feature_type = feature_type[3:]

                resource_name = ResourceByFeature[(feature_type, geometry_type)]['resource']
                bind_attr_name = ResourceByFeature[(feature_type, geometry_type)]['bind']

                resource = getattr(self.obj, resource_name, None)
                if resource is None:
                    continue

                if resource.srs.id != srs_from.id:
                    transformers.setdefault(resource_name, Transformer(srs_from.wkt, resource.srs.wkt))

                ngwfeature_data = dict(
                    layer=resource,
                    geom=feature_geometry.wkt,
                    fields={key: ensure_str(str(getattr(rrfeature, key, None)))
                            for key in dir(rrfeature)
                            if not key.startswith('_') and not callable(getattr(rrfeature, key))}
                )
                query = resource.feature_query()
                query.filter(*[(self.data.get(bind_attr_name), 'eq', rrfeature.registration_number)])
                ngwfeature = None
                for f in query():
                    ngwfeature = f
                    break
                # Если обновляем сведения
                if updated:
                    # и объект не существует, то создаём новый
                    if ngwfeature is None:
                        ngwfeature = Feature(layer=resource)
                        rr2ngw(ngwfeature, ngwfeature_data, transformer=transformers.get(resource_name, None))
                        ngwfeature_data['id'] = resource.feature_create(ngwfeature)
                    else:
                        # А если существует, то обновляем сведения о нём
                        ngwfeature_data['id'] = ngwfeature.id
                        ngwfeature = Feature(layer=resource, id=ngwfeature.id)
                        rr2ngw(ngwfeature, ngwfeature_data, transformer=transformers.get(resource_name, None))
                        ngwfeature_data['id'] = resource.feature_put(ngwfeature)
                else:
                    # А если импортируем новые сведения, то добавляем только новые объекты
                    if ngwfeature:
                        continue

                    ngwfeature = Feature(layer=resource)
                    rr2ngw(ngwfeature, ngwfeature_data, transformer=transformers.get(resource_name, None))
                    ngwfeature_data['id'] = resource.feature_create(ngwfeature)

        # NOTE: А тут возвращаем всё обратно
        shapely.speedups.enable()
