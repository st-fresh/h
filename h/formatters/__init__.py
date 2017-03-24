# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from h.formatters.annotation_flag import AnnotationFlagFormatter

__all__ = (
    'AnnotationFlagFormatter',
)

ANNOTATION_FORMATTERS_KEY = 'h.formatters.annotation'


def includeme(config):
    config.registry[ANNOTATION_FORMATTERS_KEY] = [
        AnnotationFlagFormatter
    ]

    config.add_request_method(
        lambda r: r.registry[ANNOTATION_FORMATTERS_KEY],
        name='annotation_formatters',
        reify=True)
