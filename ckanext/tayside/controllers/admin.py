from ckan.controllers.admin import AdminController
from ckan.plugins import toolkit
from ckan import logic
from ckan.common import config
import ckan.lib.uploader as uploader


class AdminController(AdminController):
    def manage_footer_logos(self):
        data = dict(toolkit.request.POST)

        if 'save' in data:
            try:
                del data['save']

                upload = uploader.get_uploader('admin')

                # Upload footer logos
                for i in range(1, 6):
                    upload.update_data_dict(data,
                                            'footer_logo_{0}_image_url'
                                            .format(i),
                                            'footer_logo_{0}_upload'.format(i),
                                            'clear_footer_logo_{0}_upload'
                                            .format(i))
                    upload.upload(uploader.get_max_image_size())

                data = toolkit.get_action('config_option_update')({}, data)
            except toolkit.ValidationError, e:
                errors = e.error_dict
                error_summary = e.error_summary
                vars = {'data': data, 'errors': errors,
                        'error_summary': error_summary}

                return toolkit.render('admin/tayside_manage_footer_logos.html',
                                      extra_vars=vars)

            ctrl =\
                'ckanext.tayside.controllers.admin:AdminController'
            toolkit.redirect_to(controller=ctrl, action='manage_footer_logos')

        schema = logic.schema.update_configuration_schema()
        data = {}

        for key in schema:
            data[key] = config.get(key)

        vars = {'data': data, 'errors': {}}

        return toolkit.render('admin/tayside_manage_footer_logos.html',
                              extra_vars=vars)
