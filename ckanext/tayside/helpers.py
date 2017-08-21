from ckan import model
from ckan.plugins import toolkit
from ckan.common import config


def _get_action(action, context_dict, data_dict):
    return toolkit.get_action(action)(context_dict, data_dict)


def get_groups():
    # Helper used on the homepage for showing groups

    data_dict = {
        'sort': 'package_count',
        'all_fields': True
    }
    groups = _get_action('group_list', {}, data_dict)
    groups = [group for group in groups if group.get('package_count') > 0]

    return groups


def get_footer_logos():
    # Helper used to display logos in footer

    footer_logos = []

    for i in range(1, 6):
        logo_image_url = config.get('footer_logo_{0}_image_url'.format(i))

        if logo_image_url:
            logo_link_url = config.get('footer_logo_{0}_link_url'.format(i))
            logo_text = config.get('footer_logo_{0}_text'.format(i))

            footer_logos.append({
                'logo_image_url': logo_image_url,
                'logo_link_url': logo_link_url,
                'logo_text': logo_text
            })

    return footer_logos
