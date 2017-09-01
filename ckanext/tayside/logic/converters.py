from ckan.logic.converters import convert_user_name_or_id_to_id


def convert_usernames_to_ids(usernames, context):
    usernames = usernames.split(',')
    usernames_ids = []

    for username in usernames:
        user_id = convert_user_name_or_id_to_id(username, context)
        usernames_ids.append(user_id)

    return ','.join(usernames_ids)


def convert_ids_to_usernames(usernames_ids, context):
    if usernames_ids:
        usernames_ids = usernames_ids.split(',')
        usernames = []

        for username_id in usernames_ids:
            session = context['session']
            model = context['model']
            result = session.query(model.User)\
                .filter_by(id=username_id).first()

            if result:
                usernames.append(result.name)

        return ','.join(usernames)
