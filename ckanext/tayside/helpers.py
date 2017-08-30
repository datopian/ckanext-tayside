from ckan import model
from ckan.plugins import toolkit
from ckan.common import config

from ckanext.tayside.model import get_downloads


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


def resource_total_views(id):
    try:
        data_dict = {'id': id, 'include_tracking': True}
        resource = _get_action('resource_show', {}, data_dict)
        tracking_summary = resource.get('tracking_summary')

        if tracking_summary:
            return tracking_summary.get('total')

        return 0
    except tookit.NotFound:
        return 0


def get_downloads_for_resources(resources):
    result = 0

    if resources:
        result = get_downloads(resources)

    return result


def order_resources(resources):
    params = dict(toolkit.request.params)
    reverse = True
    order_by = 'last_modified'

    if params and params.get('sort'):
        order_by = params.get('sort').split(' ')[0]
        reverse = params.get('sort').split(' ')[1]

        if reverse == 'asc':
            reverse = False
        elif reverse == 'desc':
            reverse = True

    for resource in resources:
        if not resource.get('last_modified'):
            resource.update({'last_modified': resource.get('created')})

    resources = sorted(resources, key=lambda x: x[order_by], reverse=reverse)

    return resources
