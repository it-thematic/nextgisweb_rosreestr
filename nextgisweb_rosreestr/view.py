# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

from nextgisweb.dynmenu import DynMenu, Label, Link, DynItem
from nextgisweb.resource import Resource, Widget
from nextgisweb.resource.scope import ResourceScope

from .util import _


PERM_UPDATE = ResourceScope.update


class RosreestrWidget(Widget):
    operation = ('create', )
    amdmod = 'ngw-rosreestr/Widget'


class RosreestrMenuExt(DynItem):
    def build(self, args):
        permissions = args.obj.permissions(args.request.user)

        if PERM_UPDATE in permissions:
            yield Link(
                'extra/import',
                _("Import"),
                lambda args: args.request.route_url("rosreestr.import", id=args.obj.id),
            )


def setup_pyramid(comp, config):
    # Расширение меню группы ресурсов
    Resource.__dynmenu__.add(RosreestrMenuExt())
