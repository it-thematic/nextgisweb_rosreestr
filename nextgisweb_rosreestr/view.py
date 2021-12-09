# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

from nextgisweb.dynmenu import Link, DynItem
from nextgisweb.pyramid import viewargs
from nextgisweb.resource import Resource, ResourceGroup,  resource_factory
from nextgisweb.resource.widget import CompositeWidget, ResourceWidget, Widget
from nextgisweb.resource.scope import ResourceScope
from pyramid import httpexceptions

from .model import Rosreestr
from .util import _


class RosreestrWidget(Widget):
    resource = Rosreestr
    operation = ('create', 'update')
    amdmod = 'ngw-rosreestr/Widget'


class RosreestrCompositeWidget(CompositeWidget):

    def __init__(self, *args, **kwargs):
        super(CompositeWidget, self).__init__(*args, **kwargs)
        self.members = []
        self.members.append(ResourceWidget(*args, **kwargs))
        self.members.append(RosreestrWidget(*args, **kwargs))


@viewargs(renderer='nextgisweb_rosreestr:templates/import.mako')
def import_data(request):
    request.resource_permission(ResourceScope.manage_children)
    return dict(obj=request.context, subtitle=_("Import rosreestr data"), maxheight=True,
                query=dict(operation='create', cls=request.GET.get('cls'),
                           parent=request.context.id))


@viewargs(renderer='json')
def import_data_widget(request):
    operation = request.GET.get('operation', None)
    resid = request.GET.get('id', None)
    clsid = request.GET.get('cls', None)
    parent_id = request.GET.get('parent', None)

    if operation == 'create':
        if resid is not None or clsid is None or parent_id is None:
            raise httpexceptions.HTTPBadRequest()

        if clsid not in Resource.registry._dict:
            raise httpexceptions.HTTPBadRequest()

        parent = Resource.query().with_polymorphic('*') \
            .filter_by(id=parent_id).one()
        owner_user = request.user
        obj = Resource.registry[clsid](parent=parent, owner_user=request.user)

    elif operation in ('update', 'delete'):
        if resid is None or clsid is not None or parent_id is not None:
            raise httpexceptions.HTTPBadRequest()

        obj = Resource.query().with_polymorphic('*') \
            .filter_by(id=resid).one()

        clsid = obj.cls
        parent = obj.parent
        owner_user = obj.owner_user

    else:
        raise httpexceptions.HTTPBadRequest()

    widget = RosreestrCompositeWidget(operation=operation, obj=obj, request=request)
    return dict(
        operation=operation, config=widget.config(), id=resid,
        cls=clsid, parent=parent.id if parent else None,
        owner_user=owner_user.id)


def setup_pyramid(comp, config):

    def _route(route_name, route_path, **kwargs):
        return config.add_route(
            'resource.' + route_name,
            '/resource/' + route_path,
            **kwargs)

    def _resource_route(route_name, route_path, **kwargs):
        return _route(
            route_name, route_path,
            factory=resource_factory,
            **kwargs)

    _resource_route('import', r'{id:\d+}/import', client=('id', )).add_view(import_data)
    _route('rrwidget', 'rrwidget', client=()).add_view(import_data_widget)

    class ImportMenuItem(DynItem):

        def build(self, args):
            if not isinstance(args.obj, ResourceGroup):
                return
            if any([isinstance(child, Rosreestr) for child in args.obj.children]):
                return

            yield Link(
                'operation/30-import', _("Import"), self._url('rosreestr'), 'material:import', True)

        def _url(self, cls):
            return lambda args: args.request.route_url(
                'resource.import', id=args.obj.id,
                _query=dict(cls=cls))

    Resource.__dynmenu__.add(ImportMenuItem())
