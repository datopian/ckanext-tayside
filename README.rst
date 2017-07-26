.. You should enable this project on travis-ci.org and coveralls.io to make
   these badges work. The necessary Travis and Coverage config files have been
   generated for you.

.. image:: https://travis-ci.org/ViderumGlobal/ckanext-tayside.svg?branch=master
    :target: https://travis-ci.org/ViderumGlobal/ckanext-tayside


===============
ckanext-tayside
===============

.. Put a description of your extension here:
   What does it do? What features does it have?
   Consider including some screenshots or embedding a video!


------------
Requirements
------------

For example, you might want to mention here which versions of CKAN this
extension works with.


------------
Installation
------------

.. Add any additional install steps to the list below.
   For example installing any non-Python dependencies or adding any required
   config settings.

To install ckanext-tayside:

1. Activate your CKAN virtual environment, for example::

     . /usr/lib/ckan/default/bin/activate

2. Install the ckanext-tayside Python package into your virtual environment::

     pip install git+https://github.com/ViderumGlobal/ckanext-tayside.git#egg=ckanext-tayside

3. Add ``tayside`` to the ``ckan.plugins`` setting in your CKAN
   config file (by default the config file is located at
   ``/etc/ckan/default/production.ini``).

4. Restart CKAN. For example if you've deployed CKAN with Apache on Ubuntu::

     sudo service apache2 reload


---------------
Config Settings
---------------

Document any optional config settings here. For example::

    # The minimum number of hours to wait before re-checking a resource
    # (optional, default: 24).
    ckanext.tayside.some_setting = some_default_value


------------------------
Development Installation
------------------------

To install ckanext-tayside for development, activate your CKAN virtualenv and
do::

    git clone https://github.com/duskobogdanovski/ckanext-tayside.git
    cd ckanext-tayside
    python setup.py develop
    pip install -r dev-requirements.txt


----------
Modify CSS
----------

This extension uses LESS for styles. All changes must be made in one of the LESS
files located in the ``ckanext-tayside/ckanext/tayside/fanstatic/less`` folder.

In order to compile those files to CSS, the `less <https://www.npmjs.com/package/less>`_
npm module is used.

First make sure that you have installed `Node.js <https://nodejs.org/en/>`_. That
will install the ``npm`` package manager. After that, open up the terminal and
change the current directory to ``ckanext-tayside/ckanext/tayside/fanstatic``.

Then run the following command that is going to install LESS::

    npm install less

After a successful installation, run the next command to compile the main less
file ``tayside.less`` to ``tayside.css``::

    ./node_modules/.bin/lessc less/tayside.less css/tayside.css

Every time there is some change in one of the less files, the upper command
needs to be run to compile those files to one css file.


-----------------
Running the Tests
-----------------

To run the tests, do::

    nosetests --nologcapture --with-pylons=test.ini

To run the tests and produce a coverage report, first make sure you have
coverage installed in your virtualenv (``pip install coverage``) then run::

    nosetests --nologcapture --with-pylons=test.ini --with-coverage --cover-package=ckanext.tayside --cover-inclusive --cover-erase --cover-tests
