# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import mock
from pyramid import testing
import pytest

from h.api import schemas


class ExampleSchema(schemas.JSONSchema):
    schema = {
        b'$schema': b'http://json-schema.org/draft-04/schema#',
        b'type': b'string',
    }


class TestJSONSchema(object):

    def test_it_returns_data_when_valid(self):
        data = "a string"

        assert ExampleSchema().validate(data) == data

    def test_it_raises_when_data_invalid(self):
        data = 123  # not a string

        with pytest.raises(schemas.ValidationError):
            ExampleSchema().validate(data)

    def test_it_sets_appropriate_error_message_when_data_invalid(self):
        data = 123  # not a string

        with pytest.raises(schemas.ValidationError) as e:
            ExampleSchema().validate(data)

        message = e.value.message
        assert message.startswith("123 is not of type 'string'")


def create_annotation_schema_validate(data):
    # 'uri' is required when creating new annotations.
    if 'uri' not in data:
        data['uri'] = 'http://example.com/example'

    schema = schemas.CreateAnnotationSchema(testing.DummyRequest())
    return schema.validate(data)


def update_annotation_schema_validate(data,
                                      existing_target_uri='',
                                      groupid=''):
    schema = schemas.UpdateAnnotationSchema(testing.DummyRequest(),
                                            existing_target_uri,
                                            groupid)
    return schema.validate(data)


@pytest.mark.parametrize('validate',
    [
        create_annotation_schema_validate,
        update_annotation_schema_validate,
    ],
    ids=[
        'CreateAnnotationSchema.validate()',
        'UpdateAnnotationSchema.validate()'
    ]
)
class TestCreateUpdateAnnotationSchema(object):

    """Shared tests for CreateAnnotationSchema and UpdateAnnotationSchema."""

    def test_it_does_not_raise_for_minimal_valid_data(self, validate):
        validate({})

    def test_it_does_not_raise_for_full_valid_data(self, validate):
        # Use all the keys to make sure that valid data for all of them passes.
        validate({
            'document': {
                'dc': {
                    'identifier': ['foo', 'bar']
                },
                'highwire': {
                    'doi': ['foo', 'bar']
                },
                'link': [
                    {
                        'href': 'foo',
                        'type': 'foo',
                    },
                    {
                        'href': 'foo',
                        'type': 'foo',
                    }
                ],
            },
            'group': 'foo',
            'permissions': {
                'admin': ['acct:foo', 'group:bar'],
                'delete': ['acct:foo', 'group:bar'],
                'read': ['acct:foo', 'group:bar'],
                'update': ['acct:foo', 'group:bar'],
            },
            'references': ['foo', 'bar'],
            'tags': ['foo', 'bar'],
            'target': [
                {
                    'selector': 'foo'
                },
                {
                    'selector': 'foo'
                },
            ],
            'text': 'foo',
            'uri': 'foo',
        })

    @pytest.mark.parametrize("input_data,error_message", [
        ({'document': False}, "document: False is not of type 'object'"),

        ({'document': {'dc': False}},
         "document.dc: False is not of type 'object'"),

        ({'document': {'dc': {'identifier': False}}},
         "document.dc.identifier: False is not of type 'array'"),

        ({'document': {'dc': {'identifier': [False]}}},
         "document.dc.identifier.0: False is not of type 'string'"),

        ({'document': {'highwire': False}},
         "document.highwire: False is not of type 'object'"),

        ({'document': {'highwire': {'doi': False}}},
         "document.highwire.doi: False is not of type 'array'"),

        ({'document': {'highwire': {'doi': [False]}}},
         "document.highwire.doi.0: False is not of type 'string'"),

        ({'document': {'link': False}},
         "document.link: False is not of type 'array'"),

        ({'document': {'link': [False]}},
         "document.link.0: False is not of type 'object'"),

        ({'document': {'link': [{}]}},
         "document.link.0: 'href' is a required property"),

        ({'document': {'link': [{'href': False}]}},
         "document.link.0.href: False is not of type 'string'"),

        ({'document': {
            'link': [
                {
                    'href': 'http://example.com',
                    'type': False
                }
            ]
        }}, "document.link.0.type: False is not of type 'string'"),

        ({'group': False}, "group: False is not of type 'string'"),

        ({'permissions': False}, "permissions: False is not of type 'object'"),

        ({'permissions': {}}, "permissions: 'read' is a required property"),

        ({'permissions': {'read': False}},
         "permissions.read: False is not of type 'array'"),

        ({'permissions': {'read': [False]}},
         "permissions.read.0: False is not of type 'string'"),

        ({'permissions': {'read': ["foo"]}},
         "permissions.read.0: u'foo' does not match '^(acct:|group:).+$'"),

        ({'references': False}, "references: False is not of type 'array'"),

        ({'references': [False]},
         "references.0: False is not of type 'string'"),

        ({'tags': False}, "tags: False is not of type 'array'"),

        ({'tags': [False]}, "tags.0: False is not of type 'string'"),

        ({'target': False}, "target: False is not of type 'array'"),

        ({'target': [False]}, "target.0: False is not of type 'object'"),

        ({'text': False}, "text: False is not of type 'string'"),

        ({'uri': False}, "uri: False is not of type 'string'"),
    ])
    def test_it_raises_for_invalid_data(self,
                                        validate,
                                        input_data,
                                        error_message):
        with pytest.raises(schemas.ValidationError) as exc:
            validate(input_data)

        assert str(exc.value) == error_message

    @pytest.mark.parametrize('field', [
        'created',
        'updated',
        'user',
        'id',
        'links',
    ])
    def test_it_removes_protected_fields(self, validate, field):
        data = {}
        data[field] = 'something forbidden'
        appstruct = validate(data)

        assert field not in appstruct
        assert field not in appstruct.get('extra', {})

    def test_it_renames_uri_to_target_uri(self, validate):
        appstruct = validate({'uri': 'http://example.com/example'})

        assert appstruct['target_uri'] == 'http://example.com/example'
        assert 'uri' not in appstruct

    def test_it_keeps_text(self, validate):
        appstruct = validate({'text': 'some annotation text'})

        assert appstruct['text'] == 'some annotation text'

    def test_it_keeps_tags(self, validate):
        appstruct = validate({'tags': ['foo', 'bar']})

        assert appstruct['tags'] == ['foo', 'bar']

    def test_it_replaces_target_with_target_selectors(self, validate):
        appstruct = validate({
            'target': [
                {
                    'foo': 'bar',  # This should be removed,
                    'selector': 'the selectors',
                },
                'this should be removed',
            ]
        })

        assert appstruct['target_selectors'] == 'the selectors'

    def test_it_extracts_document_uris_from_the_document(
            self,
            parse_document_claims,
            validate):
        target_uri = 'http://example.com/example'
        document_data = {'foo': 'bar'}

        validate({'document': document_data, 'uri': target_uri})

        parse_document_claims.document_uris_from_data.assert_called_once_with(
            document_data,
            claimant=target_uri,
        )

    def test_it_puts_document_uris_in_appstruct(self,
                                                parse_document_claims,
                                                validate):
        appstruct = validate({'document': {}})

        assert appstruct['document']['document_uri_dicts'] == (
            parse_document_claims.document_uris_from_data.return_value)

    def test_it_extracts_document_metas_from_the_document(
            self,
            parse_document_claims,
            validate):
        document_data = {'foo': 'bar'}
        target_uri = 'http://example.com/example'

        validate({'document': {'foo': 'bar'}, 'uri': target_uri})

        parse_document_claims.document_metas_from_data.assert_called_once_with(
            document_data,
            claimant=target_uri,
        )

    def test_it_does_not_pass_modified_dict_to_document_metas_from_data(
            self,
            parse_document_claims,
            validate):
        """

        If document_uris_from_data() modifies the document dict that it's
        given, the original dict (or one with the same values as it) should be
        passed t document_metas_from_data(), not the modified copy.

        """
        document = {
            'top_level_key': 'original_value',
            'sub_dict': {
                'key': 'original_value'
            }
        }

        def document_uris_from_data(document, claimant):
            document['new_key'] = 'new_value'
            document['top_level_key'] = 'new_value'
            document['sub_dict']['key'] = 'new_value'
        parse_document_claims.document_uris_from_data.side_effect = (
            document_uris_from_data)

        validate({'document': document})

        assert (
            parse_document_claims.document_metas_from_data.call_args[0][0] ==
            document)

    def test_it_puts_document_metas_in_appstruct(self,
                                                 parse_document_claims,
                                                 validate):
        appstruct = validate({'document': {}})

        assert appstruct['document']['document_meta_dicts'] == (
            parse_document_claims.document_metas_from_data.return_value)

    def test_it_clears_existing_keys_from_document(self, validate):
        """
        Any keys in the document dict should be removed.

        They're replaced with the 'document_uri_dicts' and
        'document_meta_dicts' keys.

        """
        appstruct = validate({
            'document': {
                'foo': 'bar'  # This should be deleted.
            }
        })

        assert 'foo' not in appstruct['document']

    def test_document_does_not_end_up_in_extra(self, validate):
        appstruct = validate({'document': {'foo': 'bar'}})

        assert 'document' not in appstruct.get('extra', {})

    def test_it_moves_extra_data_into_extra_sub_dict(self, validate):
        appstruct = validate({
            # Throw in all the fields, just to make sure that none of them get
            # into extra.
            'created': 'created',
            'updated': 'updated',
            'user': 'user',
            'id': 'id',
            'uri': 'uri',
            'text': 'text',
            'tags': ['gar', 'har'],
            'permissions': {'read': ['group:__world__']},
            'target': [],
            'group': '__world__',
            'references': ['parent'],

            # These should end up in extra.
            'foo': 1,
            'bar': 2,
        })

        assert appstruct['extra'] == {'foo': 1, 'bar': 2}

    def test_it_does_not_modify_extra_fields_that_are_not_sent(self, validate):
        appstruct = validate({'foo': 'bar'})

        assert 'custom' not in appstruct['extra']

    def test_it_does_not_modify_extra_fields_if_none_are_sent(self, validate):
        appstruct = validate({})

        assert not appstruct.get('extra')


class TestCreateAnnotationSchema(object):

    def test_it_raises_if_data_has_no_uri(self):
        data = self.valid_data()
        del data['uri']
        schema = schemas.CreateAnnotationSchema(testing.DummyRequest())

        with pytest.raises(schemas.ValidationError) as exc:
            schema.validate(data)

        assert exc.value.message == "uri: 'uri' is a required property"

    def test_it_raises_if_uri_is_empty_string(self):
        schema = schemas.CreateAnnotationSchema(testing.DummyRequest())

        with pytest.raises(schemas.ValidationError) as exc:
            schema.validate(self.valid_data(uri=''))

        assert exc.value.message == "uri: 'uri' is a required property"

    def test_it_sets_userid(self, config):
        config.testing_securitypolicy('acct:harriet@example.com')
        schema = schemas.CreateAnnotationSchema(testing.DummyRequest())

        appstruct = schema.validate(self.valid_data())

        assert appstruct['userid'] == 'acct:harriet@example.com'

    def test_it_inserts_empty_string_if_data_contains_no_text(self):
        schema = schemas.CreateAnnotationSchema(testing.DummyRequest())

        assert schema.validate(self.valid_data())['text'] == ''

    def test_it_inserts_empty_list_if_data_contains_no_tags(self):
        schema = schemas.CreateAnnotationSchema(testing.DummyRequest())

        assert schema.validate(self.valid_data())['tags'] == []

    def test_it_replaces_private_permissions_with_shared_False(self):
        schema = schemas.CreateAnnotationSchema(testing.DummyRequest())

        appstruct = schema.validate(self.valid_data(
            permissions={'read': ['acct:harriet@example.com']}
        ))

        assert appstruct['shared'] is False
        assert 'permissions' not in appstruct

    def test_it_replaces_shared_permissions_with_shared_True(self):
        schema = schemas.CreateAnnotationSchema(testing.DummyRequest())

        appstruct = schema.validate(self.valid_data(
            permissions={'read': ['group:__world__']},
            group='__world__'
        ))

        assert appstruct['shared'] is True
        assert 'permissions' not in appstruct

    def test_it_defaults_to_private_if_no_permissions_object_sent(self):
        schema = schemas.CreateAnnotationSchema(testing.DummyRequest())

        appstruct = schema.validate(self.valid_data())

        assert appstruct['shared'] is False

    def test_it_renames_group_to_groupid(self):
        schema = schemas.CreateAnnotationSchema(testing.DummyRequest())

        appstruct = schema.validate(self.valid_data(group='foo'))

        assert appstruct['groupid'] == 'foo'
        assert 'group' not in appstruct

    def test_it_inserts_default_groupid_if_no_group(self):
        schema = schemas.CreateAnnotationSchema(testing.DummyRequest())

        appstruct = schema.validate(self.valid_data())

        assert appstruct['groupid'] == '__world__'

    def test_it_keeps_references(self):
        schema = schemas.CreateAnnotationSchema(testing.DummyRequest())

        appstruct = schema.validate(self.valid_data(
            references=['parent id', 'parent id 2']
        ))

        assert appstruct['references'] == ['parent id', 'parent id 2']

    def test_it_inserts_empty_list_if_no_references(self):
        schema = schemas.CreateAnnotationSchema(testing.DummyRequest())

        appstruct = schema.validate(self.valid_data())

        assert appstruct['references'] == []

    def test_it_deletes_groupid_for_replies(self):
        schema = schemas.CreateAnnotationSchema(testing.DummyRequest())

        appstruct = schema.validate(self.valid_data(
            group='foo',
            references=['parent annotation id']
        ))

        assert 'groupid' not in appstruct

    def valid_data(self, **kwargs):
        """Return minimal valid data for creating a new annotation."""
        data = {
            'uri': 'http://example.com/example',
        }
        data.update(kwargs)
        return data


class TestUpdateAnnotationSchema(object):

    def test_you_cannot_change_an_annotations_group(self):
        schema = schemas.UpdateAnnotationSchema(testing.DummyRequest(), '', '')

        appstruct = schema.validate({
            'groupid': 'new-group',
            'group': 'new-group'
        })


        assert 'groupid' not in appstruct
        assert 'groupid' not in appstruct.get('extra', {})
        assert 'group' not in appstruct
        assert 'group' not in appstruct.get('extra', {})

    def test_you_cannot_change_an_annotations_userid(self):
        schema = schemas.UpdateAnnotationSchema(testing.DummyRequest(), '', '')

        appstruct = schema.validate({'userid': 'new_userid'})

        assert 'userid' not in appstruct
        assert 'userid' not in appstruct.get('extra', {})

    def test_you_cannot_change_an_annotations_references(self):
        schema = schemas.UpdateAnnotationSchema(testing.DummyRequest(), '', '')

        appstruct = schema.validate({'references': ['new_parent']})

        assert 'references' not in appstruct
        assert 'references' not in appstruct.get('extra', {})

    def test_it_replaces_private_permissions_with_shared_False(self):
        schema = schemas.UpdateAnnotationSchema(testing.DummyRequest(), '', '')

        appstruct = schema.validate({
            'permissions': {'read': ['acct:harriet@example.com']}
        })

        assert appstruct['shared'] is False
        assert 'permissions' not in appstruct
        assert 'permissions' not in appstruct.get('extras', {})

    def test_it_replaces_shared_permissions_with_shared_True(self):
        schema = schemas.UpdateAnnotationSchema(testing.DummyRequest(),
                                                '',
                                                '__world__')

        appstruct = schema.validate({
            'permissions': {'read': ['group:__world__']}
        })

        assert appstruct['shared'] is True
        assert 'permissions' not in appstruct
        assert 'permissions' not in appstruct.get('extras', {})

    def test_it_passes_existing_target_uri_to_document_uris_from_data(
            self,
            parse_document_claims):
        """
        If no 'uri' is given it should use the existing target_uri.

        If no 'uri' is given in the update request then
        document_uris_from_data() should be called with the existing
        target_uri of the annotation in the database.

        """
        document_data = {'foo': 'bar'}
        schema = schemas.UpdateAnnotationSchema(testing.DummyRequest(),
                                                mock.sentinel.target_uri,
                                                '')

        schema.validate({'document': document_data})

        parse_document_claims.document_uris_from_data.assert_called_once_with(
            document_data,
            claimant=mock.sentinel.target_uri)

    def test_it_passes_existing_target_uri_to_document_metas_from_data(
            self,
            parse_document_claims):
        """
        If no 'uri' is given it should use the existing target_uri.

        If no 'uri' is given in the update request then
        document_metas_from_data() should be called with the existing
        target_uri of the annotation in the database.

        """
        document_data = {'foo': 'bar'}
        schema = schemas.UpdateAnnotationSchema(testing.DummyRequest(),
                                                mock.sentinel.target_uri,
                                                '')

        schema.validate({'document': document_data})

        parse_document_claims.document_metas_from_data.assert_called_once_with(
            document_data,
            claimant=mock.sentinel.target_uri)


@pytest.fixture
def parse_document_claims(patch):
    return patch('h.api.schemas.parse_document_claims')