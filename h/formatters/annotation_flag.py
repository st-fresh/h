# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from zope.interface import implementer

from h import models
from h import util
from h.formatters.interfaces import IAnnotationFormatter


@implementer(IAnnotationFormatter)
class AnnotationFlagFormatter(object):
    def __init__(self, request, authenticated_user=None):
        self.session = request.db
        self.authenticated_user = authenticated_user or request.authenticated_user

        # Local cache of fetched flags.
        self._cache = {}

        # But don't allow the cache to persist after the session is closed.
        @util.db.on_transaction_end(self.session)
        def flush_cache():
            self._cache = {}

    def preload(self, ids):
        if self.authenticated_user is None:
            return

        query = self.session.query(models.Flag) \
                            .filter(models.Flag.annotation_id.in_(ids),
                                    models.Flag.user == self.authenticated_user)

        for flag in query:
            self._cache[flag.annotation_id] = True

        # Set flags which have not been found explicitely to False to indicate
        # that we already tried to load them.
        missing_ids = set(ids) - set(self._cache.keys())
        for id_ in missing_ids:
            self._cache[id_] = False

    def load(self, id_):
        if self.authenticated_user is None:
            return False

        if id_ in self._cache:
            return self._cache[id_]

        flag = self.session.query(models.Flag) \
                           .filter_by(annotation_id=id_,
                                      user=self.authenticated_user) \
                           .one_or_none()

        self._cache[id_] = (flag is not None)
        return self._cache[id_]

    def format(self, annotation):
        flagged = self.load(annotation.id)
        return {'flagged': flagged}
