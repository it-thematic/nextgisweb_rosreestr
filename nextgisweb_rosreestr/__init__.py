# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from nextgisweb.component import Component, require

from .model import Base
from .util import COMP_ID


class RosreestrComponent(Component):
    identity = COMP_ID
    metadata = Base.metadata

    @require('resource')
    def initialize(self):
        super(RosreestrComponent, self).initialize()

    def configure(self):
        super(RosreestrComponent, self).configure()

    def setup_pyramid(self, config):
        super(RosreestrComponent, self).setup_pyramid(config)

        from . import view
        from . import api

        view.setup_pyramid(self, config)
        api.setup_pyramid(self, config)


def pkginfo():
    return dict(components=dict(
        rosreestr='nextgisweb_rosreestr'))


def amd_packages():
    return (
        ('ngw-rosreestr', 'nextgisweb_rosreestr:amd/ngw-rosreestr'),
    )
