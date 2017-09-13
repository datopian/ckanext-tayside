from ckan.logic.action import get as get_core
from ckan.plugins import toolkit


@toolkit.side_effect_free
def package_show(context, data_dict):
    ''' This action is overriden so that the extra field "theme" is added.
    This is needed because when a dataset is exposed to DCAT it needs this
    field.

    Themes are coming from groups where a dataset is added to. The field
    "theme" exists in group's schema.'''

    result = get_core.package_show(context, data_dict)

    dataset_id = result.get('id')
    model = context.get('model')
    package = model.Package.get(dataset_id)
    groups = package.get_groups(group_type='group')
    themes = []

    for group in groups:
        theme = group.extras.get('theme')

        if theme:
            themes.append(theme)

    result = result.copy()
    extras = result.get('extras')

    for extra in extras:
        if extra.get('key') == 'theme':
            extra['value'] = themes
            return result

    extras.append({'key': 'theme', 'value': themes})

    return result
