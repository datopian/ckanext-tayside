from ckan import model
from ckan.plugins import toolkit


def _get_action(action, context_dict, data_dict):
    return toolkit.get_action(action)(context_dict, data_dict)


def get_groups():
    # Helper used on the homepage for showing groups

    data_dict = {
        'sort': 'package_count',
        'limit': 7,
        'all_fields': True
    }
    groups = _get_action('group_list', {}, data_dict)

    return groups
