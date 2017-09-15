from ckan.logic.action import get as get_core
from ckan.plugins import toolkit
import ckan.lib.helpers as h


@toolkit.side_effect_free
def package_show(context, data_dict):
    ''' This action is overriden so that the extra field "theme" is added.
    This is needed because when a dataset is exposed to DCAT it needs this
    field.

    Themes are coming from groups where a dataset is added to. The field
    "theme" exists in group's schema.'''

    result = get_core.package_show(context, data_dict)

    dataset_id = result.get('id')
    owner_org = result.get('owner_org')
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
    extra_theme_found = False
    extra_publisher_email_found = False
    extra_publisher_url_found = False

    if extras:
        for extra in extras:
            if extra.get('key') == 'theme':
                extra['value'] = themes
                extra_theme_found = True

            if extra.get('key') == 'publisher_email':
                extra_publisher_email_found = True
                data_dict = {'id': owner_org}
                org = toolkit.get_action('organization_show')({}, data_dict)
                organization_email = org.get('organization_email')
                extra['value'] = organization_email

            if extra.get('key') == 'publisher_url':
                extra_publisher_url_found = True
                publisher_url = h.url_for(controller='organization',
                                          action='read',
                                          id=owner_org, qualified=True)
                extra['value'] = publisher_url

        if not extra_theme_found:
            extras.append({'key': 'theme', 'value': themes})

        if not extra_publisher_email_found:
            data_dict = {'id': owner_org}
            org = toolkit.get_action('organization_show')({}, data_dict)
            organization_email = org.get('organization_email')

            if organization_email:
                extras.append({
                    'key': 'publisher_email',
                    'value': organization_email
                })

        if not extra_publisher_url_found:
            publisher_url = h.url_for(controller='organization', action='read',
                                      id=owner_org, qualified=True)
            extras.append({'key': 'publisher_url', 'value': publisher_url})

        return result
    else:
        result.update({'extras': []})
        extras = result.get('extras')

    org = toolkit.get_action('organization_show')({}, {'id': owner_org})
    organization_email = org.get('organization_email')

    if organization_email:
        extras.append({'key': 'publisher_email', 'value': organization_email})

    publisher_url = h.url_for(controller='organization', action='read',
                              id=owner_org, qualified=True)
    extras.append({'key': 'publisher_url', 'value': publisher_url})

    return result
