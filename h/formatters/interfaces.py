# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from zope.interface import Interface


class IAnnotationFormatter(Interface):
    def __init__(self, request):
        """
        Returns a new annotation formatter.

        An annotation formatter responds among other methods to
        ``format(annotation)``. This method is expected to return a dictionary,
        the base annotation dictionary is then getting merged together with all
        the configured formatters to produce the final annotation dictionary
        which will be returned back to the client as JSON.

        :param request: The pyramid request.
        :type request: ``pyramid.util.Request``
        """

    def preload(self, ids):
        """
        Batch load data based on annotation ids.

        This allows to optimize database access by calling this method with a
        list of annotation ids every time a list of annotations needs to be
        formatted.

        Calls to ``h.interfaces.IAnnotationFormatter.format`` should still be
        able to load individual annotations, but should first check a cache
        that is being initialised with calls to this method.

        :param ids: List of annotation ids based on which data should be preloaded.
        :type ids: list of unicode
        """

    def format(self, annotation):
        """
        Presents additional annotation data that will be served to API clients.

        The implementation of this method should make use of the preloading
        feature, but if data for the given annotation is not loaded it should
        be able to fetch additional data.

        :param annotation: The annotation object that needs presenting.
        :type annotation: memex.models.Annotation

        :returns: A formatted dictionary.
        :rtype: dict
        """
