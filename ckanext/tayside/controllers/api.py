from ckan.plugins import toolkit
from ckan import model
from ckan.common import c
import ckan.lib.jsonp as jsonp


class ApiController(toolkit.base.BaseController):

    @jsonp.jsonpify
    def user_autocomplete(self):
        q = toolkit.request.params.get('q', '')
        owner_org = toolkit.request.params.get('owner_org')
        limit = toolkit.request.params.get('limit', 20)
        user_list = []

        if q:
            context = {'model': model, 'session': model.Session,
                       'user': c.user, 'auth_user_obj': c.userobj}

            data_dict = {'q': q, 'limit': limit}

            user_list = toolkit.get_action('user_autocomplete')({}, data_dict)

            data_dict = {'id': owner_org}
            current_org = toolkit.get_action('organization_show')({},
                                                                  data_dict)
            current_org_users = current_org.get('users')

            # Get only the usernames
            current_org_users = [user.get('name') for user in
                                 current_org_users]

            # Exclude users that are already members in the organization
            user_list = [user for user in user_list if user.get('name')
                         not in current_org_users]

        return user_list
