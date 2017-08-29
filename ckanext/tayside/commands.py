import logging
import os

from ckan.lib.cli import CkanCommand
from ckan import model

from ckanext.googleanalytics.ga_auth import init_service, get_profile_id

from ckanext.tayside.model import init_table, update_downloads


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

                for row in results.get('rows'):
                    resources_downloads.append({
                        'resource_id': row[1],
                        'total_downloads': int(row[2])
                    })

        # If there are less than 75 resources then query all.
        if len(resources) < 75:
            results = self.service.data().ga().get(**params).execute()

            for row in results.get('rows'):
                resources_downloads.append({
                    'resource_id': row[1],
                    'total_downloads': int(row[2])
                })

        return resources_downloads
