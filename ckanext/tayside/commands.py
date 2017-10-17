import logging
import os
import datetime

from ckan.lib.cli import CkanCommand
from ckan import model
from ckan.plugins import toolkit
from ckan.controllers.admin import get_sysadmins
import ckan.lib.mailer as ckan_mailer
import ckan.lib.helpers as h

from ckanext.googleanalytics.ga_auth import init_service, get_profile_id

from ckanext.tayside.model import init_table, update_downloads
from ckanext.tayside.helpers import get_update_frequency_list


class InitDB(CkanCommand):
    ''' Initialize the local database table '''

    summary = __doc__.split('\n')[0]
    usage = __doc__
    max_args = 0
    min_args = 0

    def command(self):
        self._load_config()
        log = logging.getLogger('ckanext.tayside')
        init_table()
        log.info('Local database table initialized.')


class LoadAnalytics(CkanCommand):
    '''Parse data from Google Analytics API and store it
    in a local database

    Options:
        <token_file> token_file specifies the OAUTH credentials file
    '''

    summary = __doc__.split('\n')[0]
    usage = __doc__
    max_args = 1
    min_args = 1

    def command(self):
        self._load_config()
        log = logging.getLogger('ckanext.tayside')

        model.Session.remove()
        model.Session.configure(bind=model.meta.engine)

        self._init_ga_service()

        resources = self._get_all_resources()
        resources_downloads = self._get_resource_downloads(resources)

        for item in resources_downloads:
            update_downloads(**item)

        log.info('Resource downloads successfully imported from GA.')

    def _init_ga_service(self):
        token_file = self.args[0]

        if not os.path.exists(token_file):
            raise Exception('Cannot find the token file %s' % self.args[0])

        try:
            self.service = init_service(token_file)
        except TypeError as e:
            raise Exception('Unable to create a service: {0}'.format(e))

        self.profile_id = get_profile_id(self.service)

    def _get_all_resources(self):
        engine = model.meta.engine
        sql = 'SELECT id FROM resource;'
        result = engine.execute(sql).fetchall()
        resources = []

        if result:
            for resource in result:
                resources.append(resource[0])

        return resources

    def _get_resource_downloads(self, resources):
        resources_downloads = []

        params = {
            'ids': 'ga:' + self.profile_id,
            'start_date': '2017-08-01',
            'end_date': 'today',
            'metrics': 'ga:totalEvents',
            'dimensions': 'ga:eventAction,ga:eventLabel',
            'filters': 'ga:eventAction==ResourceDownload;'
        }

        for idx, resource in enumerate(resources):
            new_filter = 'ga:eventLabel==' + resource

            if idx < len(resources) - 1:
                new_filter += ','

            params.update({'filters': params.get('filters') + new_filter})

            # Since there is a hard limit of 4KB for a URL, we must split
            # getting data in batches of 75 resources per batch.
            if (idx + 1) % 75 == 0:

                # Remove the comma from the end
                params.update({'filters': params.get('filters')[:-1]})
                results = self.service.data().ga().get(**params).execute()

                # Reset filters for next batch.
                params.update({'filters': 'ga:eventAction==ResourceDownload;'})

                if results.get('rows'):
                    for row in results.get('rows'):
                        resources_downloads.append({
                            'resource_id': row[1],
                            'total_downloads': int(row[2])
                        })

        # If there are less than 75 resources then query all.
        if len(resources) < 75:
            results = self.service.data().ga().get(**params).execute()

            if results.get('rows'):
                for row in results.get('rows'):
                    resources_downloads.append({
                        'resource_id': row[1],
                        'total_downloads': int(row[2])
                    })

        return resources_downloads


class CheckUpdateFrequency(CkanCommand):
    ''' Check update frequency for datasets. '''

    summary = __doc__.split('\n')[0]
    usage = __doc__
    max_args = 0
    min_args = 0

    def command(self):
        self._load_config()
        self.log = logging.getLogger('ckanext.tayside')

        self.log.info('Checking update frequency started...')

        outdated_datasets = self._check_outdated_datasets()

        if len(outdated_datasets) > 0:
            self._notify_maintainers(outdated_datasets)

        self.log.info('Checking update frequency finished successfully.')

    def _days_between(self, d1, d2):
        d1 = datetime.datetime.strptime(d1, "%Y-%m-%dT%H:%M:%S.%f")
        d2 = datetime.datetime.strptime(d2, "%Y-%m-%dT%H:%M:%S.%f")

        return abs((d2 - d1).days)

    def _check_outdated_datasets(self):
        update_frequencies = get_update_frequency_list()
        datasets = toolkit.get_action('package_search')(
            {'ignore_auth': True}, {'include_private': True, 'rows': 10000000}
        )
        current_time = datetime.date.today().strftime('%Y-%m-%dT%H:%M:%S.%f')
        outdated_datasets = []

        for dataset in datasets.get('results'):
            pkg = toolkit.get_action('package_show')(
                {'ignore_auth': True}, {'id': dataset.get('id')}
            )

            current_update_frequency = pkg.get('frequency')

            if current_update_frequency in update_frequencies:
                resources = pkg.get('resources')
                outdated_resources = 0
                contact_admin = False

                if resources:
                    for resource in resources:
                        last_modified = resource.get('last_modified')

                        if resource.get('url_type') == 'upload' and\
                           last_modified is not None:

                            days_diff = self._days_between(
                                current_time, last_modified
                            )

                            if current_update_frequency == 'Daily':
                                if days_diff > 1:
                                    outdated_resources += 1

                                    if days_diff - 1 >= 7:
                                        contact_admin = True
                            elif current_update_frequency == 'Weekly':
                                if days_diff > 7:
                                    outdated_resources += 1

                                    if days_diff - 7 >= 7:
                                        contact_admin = True
                            elif current_update_frequency == 'Monthly':
                                if days_diff > 30:
                                    outdated_resources += 1

                                    if days_diff - 30 >= 7:
                                        contact_admin = True
                            elif current_update_frequency == 'Quarterly':
                                if days_diff > 90:
                                    outdated_resources += 1

                                    if days_diff - 90 >= 7:
                                        contact_admin = True
                            elif current_update_frequency == 'Biannually':
                                if days_diff > 180:
                                    outdated_resources += 1

                                    if days_diff - 180 >= 7:
                                        contact_admin = True
                            elif current_update_frequency == 'Annually':
                                if days_diff > 360:
                                    outdated_resources += 1

                                    if days_diff - 360 >= 7:
                                        contact_admin = True

                    # Only if all data (resources) in the dataset is stale
                    # it's considered as outdated
                    if outdated_resources == len(resources):
                        outdated_datasets.append({
                            'dataset': dataset,
                            'contact_admin': contact_admin
                        })

        return outdated_datasets

    def _notify_maintainers(self, outdated_datasets):
        for item in outdated_datasets:
            maintainer = item.get('dataset').get('maintainer')

            # Notify all admins of the organization the dataset belongs to if
            # dataset is outdated for more than 1 week.
            if item.get('contact_admin'):
                org = toolkit.get_action('organization_show')({}, {
                    'id': item.get('dataset').get('owner_org')
                })

                org_users = org.get('users')

                for org_user in org_users:
                    if org_user.get('capacity') == 'admin':
                        user = toolkit.get_action('user_show')({
                            'ignore_auth': True
                        }, {
                            'id': org_user.get('name')
                        })

                        recipient_email = user.get('email')
                        self._send_mail(recipient_email, user.get('name'),
                                        item.get('dataset').get('name'))
            else:
                recipient_email = item.get('dataset').get('maintainer_email')
                self._send_mail(recipient_email, maintainer,
                                item.get('dataset').get('name'))

    def _send_mail(self, recipient_email, user_name, dataset_name):
        subject = 'Outdated dataset'
        url = h.url_for(controller='package', action='read', id=dataset_name,
                        qualified=True)
        body = 'The dataset {0} is outdated. Go to {1} and make sure it\'s '\
            'updated.'.format(dataset_name, url)

        try:
            self.log.info('Notifying user {0} for dataset {1}...'.format(
                user_name, dataset_name)
            )
            ckan_mailer.mail_recipient(user_name, recipient_email, subject,
                                       body)
        except ckan_mailer.MailerException:
            self.log.error('Error notifying user {0} for dataset '
                           '{1}.'.format(user_name, dataset_name))
