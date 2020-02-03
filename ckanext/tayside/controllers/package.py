import os
import cgi
import json
import logging

from goodtables import validate
from tabulator import Stream
import redis

from ckan.lib import base
from ckan.common import c, _
from ckan import logic
import ckan.model as model
import ckan.lib.helpers as h
from ckan.plugins import toolkit
from ckan.controllers.package import PackageController as _PackageController
import ckan.lib.navl.dictization_functions as dict_fns
from ckan.common import config
from ckan.lib.redis import is_redis_available

# from ckanext.qa.sniff_format import sniff_file_format
# from ckanext.qa.lib import resource_format_scores

get_action = logic.get_action
NotAuthorized = logic.NotAuthorized
ValidationError = logic.ValidationError
clean_dict = logic.clean_dict
redirect = toolkit.redirect_to
abort = base.abort
tuplize_dict = logic.tuplize_dict
parse_params = logic.parse_params


class PackageController(_PackageController):

    def _tag_string_to_list(self, tag_string):
        ''' This method is overridden because "tag_string" that is sent through
        the form comes as an array and not as a string. In the original
        implementation this method expects a string. '''

        if isinstance(tag_string, unicode):
            tags = tag_string.split(',')

        out = []

        for tag in tags:
            out.append({'name': tag, 'state': 'active'})

        return out

    def create_metadata_package(self):

        # Handle metadata-only datasets
        if toolkit.request.params.get('metadata'):
            package_type = 'metadata-only'
            form_vars = {
                'errors': {},
                'dataset_type': package_type,
                'action': 'new',
                'error_summary': {},
                'data': {
                    'tag_string': '',
                    'group_id': None,
                    'type': package_type
                },
                'stage': ['active']
            }

            if toolkit.request.method == 'POST':
                context = {'model': model, 'session': model.Session,
                           'user': c.user, 'auth_user_obj': c.userobj}

                data_dict = clean_dict(dict_fns.unflatten(
                    tuplize_dict(parse_params(toolkit.request.POST))))
                data_dict['type'] = package_type

                if 'tag_string' in data_dict:
                    data_dict['tags'] = self._tag_string_to_list(
                        data_dict['tag_string'])

                try:
                    package = get_action('package_create')(context, data_dict)

                    url = h.url_for(controller='package', action='read',
                                    id=package['name'])

                    redirect(url)
                except NotAuthorized:
                    abort(403, _('Unauthorized to create a dataset.'))
                except ValidationError, e:
                    errors = e.error_dict
                    error_summary = e.error_summary

                    form_vars = {
                        'errors': errors,
                        'dataset_type': package_type,
                        'action': 'new',
                        'error_summary': error_summary,
                        'stage': ['active']
                    }

                    form_vars['data'] = data_dict

                    extra_vars = {
                        'form_vars': form_vars,
                        'form_snippet': 'package/new_package_form.html',
                        'dataset_type': package_type
                    }

                    return toolkit.render('package/new.html',
                                          extra_vars=extra_vars)
            else:
                return self.new()
        else:
            return self.new()

    def dataset_edit(self, id, data=None, errors=None, error_summary=None):

        # This must be set to 'edit' otherwise a 'satges' form is going to be
        # rendered
        c.form_style = 'edit'

        return self.edit(id, data=data, errors=errors,
                         error_summary=error_summary)

    def validate_resource(self, id):
        if toolkit.request.method == 'POST':
            data = dict_fns.unflatten(
                tuplize_dict(parse_params(toolkit.request.POST))
            )
            check_schema = toolkit.request.params.get('check_schema')
            upload_data = toolkit.request.params.get('upload_data')
            file_path = data.get('file_path')

            # Logic for validating a resource against a specified schema
            if check_schema:
                schema = {
                    'fields': []
                }

                fields = data.get('field_name')
                field_type = data.get('field_type')

                # Schema is populated from data entered by the user
                for i, field in enumerate(fields):
                    schema['fields'].append({
                        'name': field,
                        'type': field_type[i]
                    })

                # File is validated with Goodtables
                report = validate(file_path, schema=schema)

                log = logging.getLogger('ckanext.tayside')

                # Score is calculated based on Sir Tim Berners-Lee's five star
                # of openness
                sniffed_format = sniff_file_format(file_path, log)
                score = resource_format_scores().get(sniffed_format['format'])

                vars = {
                    'report': report,
                    'pkg_name': id,
                    'stars': score,
                    'file_path': file_path
                }

                return toolkit.render(
                    'tayside/package/validate_resource.html',
                    extra_vars=vars
                )
            elif upload_data:
                # Handles creating a resource in CKAN

                # Metadata for the resource is stored in Redis
                r = redis.StrictRedis()
                data = json.loads(r.get(file_path))
                data['package_id'] = id

                # Dataset's state is changed from 'draft' to 'active'
                toolkit.get_action('package_patch')({}, {
                    'id': id,
                    'state': 'active'
                })

                # FieldStorage instance is created which is needed to upload
                # the file to Filestore and Datastore
                fs = cgi.FieldStorage()
                fs.file = fs.make_file()
                fs.filename = data.get('url')

                f = open(file_path, 'r')
                fs.file.write(f.read())
                fs.file.seek(0)
                f.close()

                data['upload'] = fs

                try:
                    toolkit.get_action('resource_create')({}, data)
                except Exception as e:
                    vars = {
                        'upload_error': 'An error occured while creating the '
                        'resource.',
                        'pkg_name': id
                    }

                    return toolkit.render(
                        'tayside/package/validate_resource.html',
                        extra_vars=vars
                    )

                # File is uploaded on Filestore, and now it is safe to be
                # removed from the temporary location
                os.remove(file_path)

                toolkit.redirect_to(controller='package', action='read', id=id)
            else:
                is_upload = isinstance(data.get('upload'), cgi.FieldStorage)
                supported_formats = ['csv', 'tsv', 'xls', 'xlsx', 'ods']
                current_format = data.get('url').split('.')[-1]

                if is_upload:
                    if current_format in supported_formats:
                        # Logic for storing the file locally and extracting
                        # it's headers (fields)
                        storage_path = config.get('ckan.storage_path')
                        file_path = storage_path + '/' + data.get('url')

                        # Read the file
                        buffer = data.get('upload').file
                        buffer.seek(0)

                        # Write the file locally
                        f = open(file_path, 'w')
                        f.write(buffer.read())
                        f.close()

                        # Inspect the headers (fields) of the file
                        with Stream(file_path, headers=1) as stream:
                            fields = stream.headers

                        vars = {
                            'fields': fields,
                            'pkg_name': id,
                            'file_path': file_path
                        }

                        if is_redis_available():
                            # Store the metadata of the resource in Redis for
                            # later usage
                            r = redis.StrictRedis()
                            resource_data = {
                                'name': data.get('name'),
                                'description': data.get('description'),
                                'format': data.get('format'),
                                'url': data.get('url'),
                            }

                            r.set(file_path, json.dumps(resource_data))

                            # Store it for 1 day
                            r.expire(file_path, 86400)
                        else:
                            return toolkit.render(
                                'tayside/package/validate_resource.html',
                                {
                                    'redis_error': 'Redis not available'
                                }
                            )

                        return toolkit.render(
                            'tayside/package/validate_resource.html',
                            extra_vars=vars
                        )
                    else:
                        vars = {
                            'format_error': 'Format not supported.',
                            'pkg_name': id
                        }

                        return toolkit.render(
                            'tayside/package/validate_resource.html',
                            extra_vars=vars
                        )

                vars = {
                    'format_error': 'No file provided for validation.',
                    'pkg_name': id
                }

                return toolkit.render(
                    'tayside/package/validate_resource.html',
                    extra_vars=vars
                )
        else:
            return toolkit.render(
                'tayside/package/validate_resource.html',
                {'pkg_name': id}
            )
