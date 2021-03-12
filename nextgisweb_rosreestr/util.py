# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from nextgisweb.env import env
from nextgisweb.i18n import trstring_factory

COMP_ID = 'rosreestr'
_ = trstring_factory(COMP_ID)


def find_bind_attribure(resource, keyname=None):
    """
    Функция поиска связывающего атрибута в ресурсе

    :param FeatureLayer resource: ресурс - набор векторных данных
    :param str keyname: имя атрибута для поиска. Если не задано, то
    :return:
    """
    if resource is None:
        return None
    if keyname is None:
        keyname = env.rosreestr.bind_attribute
    fields = {field.keyname: field for field in resource.fields}
    return fields[keyname].to_dict() if keyname in fields else None
