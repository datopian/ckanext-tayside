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
        toolkit.add_ckan_admin_tab(config_, 'ckanext_tayside_footer_logos',
                                   'Footer logos')

    # IRoutes

    def before_map(self, map):
        package_controller =\
            'ckanext.tayside.controllers.package:PackageController'
        admin_controller =\
            'ckanext.tayside.controllers.admin:AdminController'

        map.connect('/dataset/new', controller=package_controller,
                    action='create_metadata_package')
        map.connect('ckanext_tayside_footer_logos',
                    '/ckan-admin/manage_footer_logos',
                    controller=admin_controller, action='manage_footer_logos',
                    ckan_icon='wrench')

        return map

    # IDatasetForm

    def package_types(self):
        return ['metadata-only']

    # ITemplateHelpers

    def get_helpers(self):
        return {
            'tayside_get_groups': helpers.get_groups,
            'tayside_get_footer_logos': helpers.get_footer_logos,
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
            'config_option_update': update_actions.config_option_update
        }
