import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckan.lib.plugins import (DefaultPermissionLabels, DefaultGroupForm,
                              DefaultTranslation)
from ckan.common import c
from ckan.lib.base import BaseController
from ckan.common import config

from ckanext.tayside import helpers
import ckanext.tayside.logic.action.update as update_actions
import ckanext.tayside.logic.action.get as get_actions
from ckanext.tayside.logic import validators as tayside_validators
from ckanext.tayside.logic import converters as tayside_converters


# There is a bug in CKAN where header keys and values for CORS are using
# unicode, and that causes problem in uwsgi. This monkey patch fixes that.
def set_cors_headers_for_response(response):
    u'''
    Set up Access Control Allow headers if either origin_allow_all is True, or
    the request Origin is in the origin_whitelist.
    '''

    cors_origin_allowed = None
    if toolkit.asbool(config.get('ckan.cors.origin_allow_all')):
        cors_origin_allowed = '*'
    elif config.get('ckan.cors.origin_whitelist') and \
            toolkit.request.headers.get('Origin') \
            in config['ckan.cors.origin_whitelist'].split(' '):
        # set var to the origin to allow it.
        cors_origin_allowed = toolkit.request.headers.get('Origin')

    if cors_origin_allowed is not None:
        response.headers['Access-Control-Allow-Origin'] = \
            cors_origin_allowed
        response.headers['Access-Control-Allow-Methods'] = \
            'POST, PUT, GET, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = \
            'X-CKAN-API-KEY, Authorization, Content-Type'

    return response


def __after__(self, action, **params):
    set_cors_headers_for_response(toolkit.response)


BaseController.__after__ = __after__


class TaysidePlugin(plugins.SingletonPlugin, toolkit.DefaultDatasetForm,
                    DefaultPermissionLabels, DefaultTranslation):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IRoutes, inherit=True)
    plugins.implements(plugins.IDatasetForm, inherit=True)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IActions)
    plugins.implements(plugins.IPackageController, inherit=True)
    plugins.implements(plugins.IPermissionLabels)
    plugins.implements(plugins.ITranslation)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'tayside')
        toolkit.add_ckan_admin_tab(config_, 'ckanext_tayside_footer_logos',
                                   'Organization Links')

    # IRoutes

    def before_map(self, map):
        package_controller =\
            'ckanext.tayside.controllers.package:PackageController'
        admin_controller =\
            'ckanext.tayside.controllers.admin:AdminController'
        api_controller =\
            'ckanext.tayside.controllers.api:ApiController'

        map.connect('/dataset/new', controller=package_controller,
                    action='create_metadata_package')
        map.connect('dataset_edit', '/dataset/edit/{id}',
                    controller=package_controller, action='dataset_edit',
                    ckan_icon='pencil-square-o')
        map.connect('/dataset/new_resource/{id}/validate',
                    controller=package_controller,
                    action='validate_resource')
        map.connect('ckanext_tayside_footer_logos',
                    '/ckan-admin/manage_footer_logos',
                    controller=admin_controller, action='manage_footer_logos',
                    ckan_icon='building-o')
        map.connect('/api/2/util/tayside_user/autocomplete',
                    controller=api_controller, action='user_autocomplete')

        return map

    # IDatasetForm

    def _modify_package_schema(self, schema):
        ignore_empty = toolkit.get_validator('ignore_empty')
        convert_to_extras = toolkit.get_converter('convert_to_extras')
        not_empty = toolkit.get_validator('not_empty')
        email_validator = toolkit.get_validator('email_validator')
        not_missing = toolkit.get_validator('not_missing')
        tag_name_validator = toolkit.get_validator('tag_name_validator')

        schema.update({
            'allowed_users': [ignore_empty,
                              tayside_validators.user_names_exists,
                              tayside_validators.users_in_org_exists,
                              tayside_converters.convert_usernames_to_ids,
                              convert_to_extras],
            'title': [not_empty, unicode],
            'notes': [not_empty, unicode],
            'author': [not_empty, unicode],
            'author_email': [not_empty, unicode, email_validator],
            'maintainer': [not_empty, unicode],
            'maintainer_email': [not_empty, unicode, email_validator],
            'frequency': [ignore_empty, unicode, convert_to_extras]
        })

        schema.get('tags').update({
            'name': [not_missing, not_empty, unicode]
        })

        return schema

    def create_package_schema(self):
        not_empty = toolkit.get_validator('not_empty')
        tag_string_convert = toolkit.get_validator('tag_string_convert')

        schema = super(TaysidePlugin, self).create_package_schema()
        schema = self._modify_package_schema(schema)

        schema.update({
            'tag_string': [not_empty],
        })

        return schema

    def update_package_schema(self):
        ignore_empty = toolkit.get_validator('ignore_empty')

        schema = super(TaysidePlugin, self).update_package_schema()
        schema = self._modify_package_schema(schema)

        schema.update({
            'tag_string': [ignore_empty],
        })

        return schema

    def show_package_schema(self):
        schema = super(TaysidePlugin, self).show_package_schema()
        ignore_missing = toolkit.get_validator('ignore_missing')
        convert_from_extras = toolkit.get_converter('convert_from_extras')

        schema.update({
            'allowed_users': [convert_from_extras,
                              tayside_converters.convert_ids_to_usernames,
                              ignore_missing],
            'frequency': [convert_from_extras, ignore_missing]
        })

        return schema

    def package_types(self):
        return ['dataset', 'metadata-only']

    # ITemplateHelpers

    def get_helpers(self):
        return {
            'tayside_get_groups': helpers.get_groups,
            'tayside_get_footer_logos': helpers.get_footer_logos,
            'tayside_resource_total_views': helpers.resource_total_views,
            'tayside_get_downloads_for_resources':
            helpers.get_downloads_for_resources,
            'tayside_order_resources': helpers.order_resources,
            'tayside_get_tags': helpers.get_tags,
            'tayside_organization_image_url': helpers.organization_image_url,
            'tayside_get_update_frequency_list':
            helpers.get_update_frequency_list,
        }

    # IConfigurer

    def update_config_schema(self, schema):
        ignore_missing = toolkit.get_validator('ignore_missing')
        validators = [ignore_missing, unicode]

        schema.update({
            'twitter_username': validators,
            'clear_hero_image_upload': validators,
            'hero_image_url': validators,
            'hero_image_upload': validators,
            'hero_image_license_text': validators,
            'site_symbol_url': validators,
            'site_symbol_upload': validators,
            'clear_site_symbol_upload': validators
        })

        for i in range(1, 6):
            schema.update({'footer_logo_{0}_image_url'.format(i): validators})
            schema.update({'footer_logo_{0}_link_url'.format(i): validators})
            schema.update({'footer_logo_{0}_text'.format(i): validators})
            schema.update({'footer_logo_{0}_upload'.format(i): validators})
            schema.update({
                'clear_footer_logo_{0}_upload'.format(i): validators
            })

        return schema

    # IActions

    def get_actions(self):
        return {
            'config_option_update': update_actions.config_option_update,
            'package_show': get_actions.package_show
        }

    # IPackageController

    def before_search(self, search_params):
        fq = search_params.get('fq', '')

        if 'dataset_type:dataset' in fq:
            fq = fq.replace('dataset_type:dataset',
                            'dataset_type: (dataset OR '
                            'metadata-only)')
            search_params.update({'fq': fq})

        return search_params

    # IPermissionLabels

    def get_dataset_labels(self, dataset_obj):
        pkg = toolkit.get_action('package_show')({'ignore_auth': True},
                                                 {'id': dataset_obj.id})
        allowed_users = pkg.get('allowed_users', [])

        # Allow users that don't belong to an organization to have access to a
        # private dataset if they are whitelisted.
        #
        # allowed_users is a dataset schema field that contains a list of
        # user ids.
        if pkg.get('private') and allowed_users:
            allowed_users = allowed_users.split(',')
            labels = []

            for user in allowed_users:
                user = toolkit.get_action('user_show')({}, {'id': user})
                labels.append(u'allowed_user-{0}'.format(user.get('id')))

            return labels

        return super(TaysidePlugin, self).get_dataset_labels(dataset_obj)

    def get_user_dataset_labels(self, user_obj):
        labels = super(TaysidePlugin, self).get_user_dataset_labels(user_obj)

        # Label the current user as an allowed user. If this label matches
        # with one of the "allowed_user-*" labels from get_dataset_labels()
        # than the user will have access to the dataset.
        if user_obj:
            labels.append(u'allowed_user-{0}'.format(user_obj.id))

        return labels


class TaysideGroupSchemaPlugin(plugins.SingletonPlugin, DefaultGroupForm):
    plugins.implements(plugins.IGroupForm, inherit=True)

    # IGroupForm

    def group_types(self):
        return ['group']

    def form_to_db_schema(self):
        convert_to_extras = toolkit.get_converter('convert_to_extras')
        ignore_missing = toolkit.get_validator('ignore_missing')

        schema = super(TaysideGroupSchemaPlugin, self).form_to_db_schema()
        schema.update({
            'theme': [convert_to_extras, ignore_missing, unicode]
        })

        return schema

    def db_to_form_schema(self):
        convert_from_extras = toolkit.get_converter('convert_from_extras')
        ignore_missing = toolkit.get_validator('ignore_missing')
        not_empty = toolkit.get_validator('not_empty')

        schema = super(TaysideGroupSchemaPlugin, self).form_to_db_schema()
        schema.update({
            'theme': [convert_from_extras, ignore_missing],
            'num_followers': [not_empty],
            'package_count': [ignore_missing]
        })

        return schema
