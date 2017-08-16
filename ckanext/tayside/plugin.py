import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit

from ckanext.tayside import helpers


class TaysidePlugin(plugins.SingletonPlugin, toolkit.DefaultDatasetForm):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IRoutes, inherit=True)
    plugins.implements(plugins.IDatasetForm, inherit=True)
    plugins.implements(plugins.ITemplateHelpers)

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
