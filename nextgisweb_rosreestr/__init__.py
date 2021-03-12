# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from nextgisweb.component import Component, require
from nextgisweb.lib.config import Option

from .model import Base, RosreestrScope
from .util import COMP_ID


class RosreestrComponent(Component):
    identity = COMP_ID
    metadata = Base.metadata

    @require('resource')
    def initialize(self):
        self.bind_attribute = self.options['bind_attribute']
        super(RosreestrComponent, self).initialize()

    def configure(self):
        super(RosreestrComponent, self).configure()

    def setup_pyramid(self, config):
        super(RosreestrComponent, self).setup_pyramid(config)

        from . import api
        from . import view

        api.setup_pyramid(self, config)
        view.setup_pyramid(self, config)

    option_annotations = (
        Option('bind_attribute', str, default='registration_number', doc='Name of field for bind'),
    )


def pkginfo():
    return dict(components=dict(
        rosreestr='nextgisweb_rosreestr'))


def amd_packages():
    return (
        ('ngw-rosreestr', 'nextgisweb_rosreestr:amd/ngw-rosreestr'),
    )
