from ckan.tests import helpers as test_helpers, factories
from ckan import plugins
from ckan.common import config

from ckanext.tayside import helpers as tayside_helpers
from ckanext.tayside.model import init_table


class ActionBase(object):
    @classmethod
    def setup_class(self):
        if not plugins.plugin_loaded('tayside'):
            plugins.load('tayside')

    def setup(self):
        test_helpers.reset_db()
        init_table()

    @classmethod
    def teardown_class(self):
        if plugins.plugin_loaded('tayside'):
            plugins.unload('tayside')


class TestHelpers(ActionBase):
    def test_get_groups(self):
        group1 = factories.Group()
        group2 = factories.Group()
        org = factories.Organization()

        dataset_required_fields = {
            'maintainer': 'Aleksandar',
            'maintainer_email': 'test@test.com',
            'author': 'Aleksandar',
            'author_email': 'test@test.com',
            'tag_string': 'test',
            'owner_org': org.get('id')
        }

        for i in range(1):
            dataset_required_fields.update({
                'groups': [{'id': group1.get('id')}]
            })
            dataset = factories.Dataset(**dataset_required_fields)

        for i in range(3):
            dataset_required_fields.update({
                'groups': [{'id': group2.get('id')}]
            })
            dataset = factories.Dataset(**dataset_required_fields)

        groups = tayside_helpers.get_groups()

        assert groups[0].get('id') == group2.get('id')
        assert groups[1].get('id') == group1.get('id')
        assert groups[0].get('package_count') > groups[1].get('package_count')

    def test_get_footer_logos(self):
        config['footer_logo_1_image_url'] = 'http://example.com/image.png'
        config['footer_logo_1_link_url'] = 'http://google.com'
        config['footer_logo_1_text'] = 'some text'

        logos = tayside_helpers.get_footer_logos()

        assert len(logos) == 1
        assert logos[0].get('logo_image_url') ==\
            config['footer_logo_1_image_url']
        assert logos[0].get('logo_link_url') ==\
            config['footer_logo_1_link_url']
        assert logos[0].get('logo_text') ==\
            config['footer_logo_1_text']

    def test_resource_total_views(self):
        org = factories.Organization()
        dataset_required_fields = {
            'maintainer': 'Aleksandar',
            'maintainer_email': 'test@test.com',
            'author': 'Aleksandar',
            'author_email': 'test@test.com',
            'tag_string': 'test',
            'owner_org': org.get('id')
        }
        dataset = factories.Dataset(**dataset_required_fields)
        resource = factories.Resource(package_id=dataset.get('id'))

        total_views = tayside_helpers.resource_total_views(resource.get('id'))

        assert total_views == 0

    def test_get_downloads_for_resources(self):
        org = factories.Organization()
        dataset_required_fields = {
            'maintainer': 'Aleksandar',
            'maintainer_email': 'test@test.com',
            'author': 'Aleksandar',
            'author_email': 'test@test.com',
            'tag_string': 'test',
            'owner_org': org.get('id')
        }
        dataset = factories.Dataset(**dataset_required_fields)
        resources = []

        for x in range(3):
            resource = factories.Resource(package_id=dataset.get('id'))
            resources.append(resource)

        downloads = tayside_helpers.get_downloads_for_resources(resources)

        assert downloads == 0

    def test_order_resources(self):
        org = factories.Organization()
        dataset_required_fields = {
            'maintainer': 'Aleksandar',
            'maintainer_email': 'test@test.com',
            'author': 'Aleksandar',
            'author_email': 'test@test.com',
            'tag_string': 'test',
            'owner_org': org.get('id')
        }
        dataset = factories.Dataset(**dataset_required_fields)
        resources = []

        for x in range(3):
            resource = factories.Resource(
                name='name-' + str(x),
                package_id=dataset.get('id')
            )
            resources.append(resource)

        self._mock_pylons()

        ordered_resources = tayside_helpers.order_resources(resources)

        assert len(ordered_resources) == 3
        assert ordered_resources[0].get('name') == 'name-2'
        assert ordered_resources[1].get('name') == 'name-1'
        assert ordered_resources[2].get('name') == 'name-0'

    def _mock_pylons(self):
        from paste.registry import Registry
        import pylons
        from pylons.util import AttribSafeContextObj
        import ckan.lib.app_globals as app_globals
        from ckan.lib.cli import MockTranslator
        from ckan.config.routing import make_map
        from pylons.controllers.util import Request, Response
        from routes.util import URLGenerator

        class TestPylonsSession(dict):
            last_accessed = None

            def save(self):
                pass

        registry = Registry()
        registry.prepare()

        context_obj = AttribSafeContextObj()
        registry.register(pylons.c, context_obj)

        app_globals_obj = app_globals.app_globals
        registry.register(pylons.g, app_globals_obj)

        request_obj = Request(dict(HTTP_HOST="nohost", REQUEST_METHOD="GET"))
        registry.register(pylons.request, request_obj)

        translator_obj = MockTranslator()
        registry.register(pylons.translator, translator_obj)

        registry.register(pylons.response, Response())
        mapper = make_map()
        registry.register(pylons.url, URLGenerator(mapper, {}))
        registry.register(pylons.session, TestPylonsSession())

    def test_get_tags(self):
        tags = tayside_helpers.get_tags()

        assert len(tags) == 10

    def test_organization_image_url(self):
        org = factories.Organization(image_url='http://kitten.com')
        image_url = tayside_helpers.organization_image_url(org.get('id'))

        assert image_url == 'http://kitten.com'

    def test_get_update_frequency_list(self):
        frequency_list = tayside_helpers.get_update_frequency_list()

        assert frequency_list == [
            'Daily',
            'Weekly',
            'Monthly',
            'Quarterly',
            'Biannually',
            'Annually',
            'As Needed',
            'Irregular',
            'Not Planned',
            'Unknown'
        ]
