import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit

from ckanext.tayside import helpers
import ckanext.tayside.logic.action.update as update_actions


class TaysidePlugin(plugins.SingletonPlugin, toolkit.DefaultDatasetForm):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IRoutes, inherit=True)
    plugins.implements(plugins.IDatasetForm, inherit=True)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IActions)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'tayside')

    # IRoutes

    def before_map(self, map):
        package_controller =\
            'ckanext.tayside.controllers.package:PackageController'

        map.connect('/dataset/new', controller=package_controller,
                    action='create_metadata_package')

        return map

    # IDatasetForm

    def package_types(self):
        return ['metadata-only']

    # ITemplateHelpers

    def get_helpers(self):
        return {
            'tayside_get_groups': helpers.get_groups
        }

    # IConfigurer

    def update_config_schema(self, schema):
        ignore_missing = toolkit.get_validator('ignore_missing')

        schema.update({
            'twitter_username': [ignore_missing, unicode],
            'clear_hero_image_upload': [ignore_missing, unicode],
            'hero_image_url': [ignore_missing, unicode],
            'hero_image_upload': [ignore_missing, unicode],
            'hero_image_license_text': [ignore_missing, unicode],
            'site_symbol_url': [ignore_missing, unicode],
            'site_symbol_upload': [ignore_missing, unicode],
            'clear_site_symbol_upload': [ignore_missing, unicode]
        })

        return schema

    # IActions

    def get_actions(self):
        return {
            'config_option_update': update_actions.config_option_update
        }
