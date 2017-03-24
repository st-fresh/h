# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from sqlalchemy.orm import subqueryload

from memex import resources
from memex.interfaces import IGroupService

from h import models
from h import presenters
from h import storage


class AnnotationJSONPresentationService(object):
    def __init__(self, session, formatters, group_svc, links_svc):
        self.session = session
        self.formatters = formatters
        self.group_svc = group_svc
        self.links_svc = links_svc

    def present(self, annotation_resource):
        presenter = presenters.AnnotationJSONPresenter(annotation_resource)

        data = presenter.asdict()
        for formatter in self.formatters:
            data.update(formatter.format(annotation_resource.annotation))

        return data

    def present_all(self, annotation_ids):
        def eager_load_documents(query):
            return query.options(
                subqueryload(models.Annotation.document))

        annotations = storage.fetch_ordered_annotations(
            self.session, annotation_ids, query_processor=eager_load_documents)

        # preload formatters, so they can optimize database access
        for formatter in self.formatters:
            formatter.preload(annotation_ids)

        return [self.present(
                    resources.AnnotationResource(ann, self.group_svc, self.links_svc))
                for ann in annotations]

    def format(self, annotation):
        data = {}
        for formatter in self.formatters:
            data.update(formatter.format(annotation))
        return data


def annotation_json_presentation_service_factory(context, request):
    formatters = [f(request) for f in request.annotation_formatters]
    group_svc = request.find_service(IGroupService)
    links_svc = request.find_service(name='links')
    return AnnotationJSONPresentationService(request.db,
                                             formatters,
                                             group_svc,
                                             links_svc)
