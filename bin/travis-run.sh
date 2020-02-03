#!/bin/sh -e

nosetests --ckan \
          --nologcapture \
          --with-pylons=test.travis.ini \
          --with-coverage \
          --cover-package=ckanext.tayside \
          --cover-inclusive \
          --cover-erase \
          --cover-tests
