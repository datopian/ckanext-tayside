#!/bin/bash
set -e
set -x

echo "This is travis-build.bash..."

echo "Installing the packages that CKAN requires..."
sudo apt-get update -qq
sudo apt-get install postgresql-$PGVERSION solr-jetty

echo "Installing CKAN and its Python dependencies..."
git clone https://github.com/ckan/ckan
cd ckan
git checkout ckan-2.7.0
python setup.py develop
# Travis has an issue with older version of psycopg2 (2.4.5)
sed -i 's/psycopg2==2.4.5/psycopg2==2.7.3.2/' requirements.txt
pip install -r requirements.txt
pip install -r dev-requirements.txt
cd -

echo "Creating the PostgreSQL user and database..."
sudo -u postgres psql -c "CREATE USER ckan_default WITH PASSWORD 'pass';"
sudo -u postgres psql -c 'CREATE DATABASE ckan_test WITH OWNER ckan_default;'

echo "Setting up Solr..."
# Solr is multicore for tests on ckan master, but it's easier to run tests on
# Travis single-core. See https://github.com/ckan/ckan/issues/2972
sed -i -e 's/solr_url.*/solr_url = http:\/\/127.0.0.1:8983\/solr/' ckan/test-core.ini
printf "NO_START=0\nJETTY_HOST=127.0.0.1\nJETTY_PORT=8983\nJAVA_HOME=$JAVA_HOME" | sudo tee /etc/default/jetty
sudo cp ckan/ckan/config/solr/schema.xml /etc/solr/conf/schema.xml
sudo service jetty restart

echo "Initialising the database..."
cd ckan
paster db init -c test-core.ini
cd -

echo "Installing ckanext-tayside and its requirements..."
python setup.py develop
pip install -r dev-requirements.txt
pip install -r requirements.txt

echo "Moving test.ini into a subdir..."
mkdir subdir
mv test.ini subdir

echo "Installing ckanext-googleanalytics and its requirements..."
git clone https://github.com/ckan/ckanext-googleanalytics
cd ckanext-googleanalytics
python setup.py develop
pip install -r requirements.txt
pip install oauth2client
cd -

echo "Installing ckanext-report..."
git clone https://github.com/datagovuk/ckanext-report
cd ckanext-report
python setup.py develop
cd -

echo "Installing ckanext-archiver and its requirements..."
git clone https://github.com/ViderumGlobal/ckanext-archiver
cd ckanext-archiver
git checkout v1.0.4-ckan-2.7
python setup.py develop
pip install -r requirements.txt
cd -

echo "travis-build.bash is done."
