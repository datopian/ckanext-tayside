from ckan.logic.action import update as update_core
import ckan.lib.uploader as uploader


def config_option_update(context, data_dict):
    upload = uploader.get_uploader('admin')
    upload.update_data_dict(data_dict, 'hero_image_url', 'hero_image_upload',
                            'clear_hero_image_upload')
    upload.update_data_dict(data_dict, 'site_symbol_url', 'site_symbol_upload',
                            'clear_site_symbol_upload')
    upload.upload(uploader.get_max_image_size())

    return update_core.config_option_update(context, data_dict)
