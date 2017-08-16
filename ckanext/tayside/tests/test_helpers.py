from ckan.tests import helpers, factories
from ckan import plugins


class ActionBase(object):
    @classmethod
    def setup_class(self):
        if not plugins.plugin_loaded('tayside'):
            plugins.load('tayside')

    def setup(self):
        helpers.reset_db()

    @classmethod
    def teardown_class(self):
        if plugins.plugin_loaded('tayside'):
            plugins.unload('tayside')


class TestHelpers(ActionBase):
    def test_get_groups(self):
        group1 = factories.Group()
        group1 = factories.Group()
