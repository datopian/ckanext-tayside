from ckan.tests import helpers as test_helpers, factories
from ckan import plugins

from ckanext.tayside import helpers as tayside_helpers


class ActionBase(object):
    @classmethod
    def setup_class(self):
        if not plugins.plugin_loaded('tayside'):
            plugins.load('tayside')

    def setup(self):
        test_helpers.reset_db()

    @classmethod
    def teardown_class(self):
        if plugins.plugin_loaded('tayside'):
            plugins.unload('tayside')


class TestHelpers(ActionBase):
    def test_get_groups(self):
        group1 = factories.Group()
        group2 = factories.Group()

        for i in range(1):
            dataset = factories.Dataset(groups=[{'id': group1.get('id')}])

        for i in range(3):
            dataset = factories.Dataset(groups=[{'id': group2.get('id')}])

        groups = tayside_helpers.get_groups()

        assert groups[0].get('id') == group2.get('id')
        assert groups[1].get('id') == group1.get('id')
        assert groups[0].get('package_count') > groups[1].get('package_count')
