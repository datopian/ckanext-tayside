from sqlalchemy import Table, Column, Integer, String, MetaData
from sqlalchemy.sql import select
from sqlalchemy import func

from ckan import model

cached_tables = {}


def init_table():
    metadata = MetaData()
    table_name = 'ckanext_tayside_resource_downloads'
    package_stats = Table(table_name, metadata,
                          Column('resource_id', String(60),
                                 primary_key=True),
                          Column('total_downloads', Integer))
    metadata.create_all(model.meta.engine)


def get_table(name):
    if name not in cached_tables:
        meta = MetaData()
        meta.reflect(bind=model.meta.engine)
        table = meta.tables[name]
        cached_tables[name] = table
    return cached_tables[name]


def update_downloads(resource_id, total_downloads):
    table = get_table('ckanext_tayside_resource_downloads')
    id_col_name = 'resource_id'
    id_col = getattr(table.c, id_col_name)
    s = select([func.count(id_col)],
               id_col == resource_id)
    connection = model.Session.connection()
    count = connection.execute(s).fetchone()
    engine = model.meta.engine

    if count and count[0]:
        engine.execute(table.update()
                       .where(id_col == resource_id)
                       .values(total_downloads=total_downloads))
    else:
        values = {id_col_name: resource_id, 'total_downloads': total_downloads}
        engine.execute(table.insert().values(**values))


def get_downloads(resources):
    engine = model.meta.engine
    sql = '''SELECT sum(total_downloads)
    FROM ckanext_tayside_resource_downloads
    WHERE '''

    for idx, resource in enumerate(resources):
        sql += 'resource_id=\'' + resource.get('id') + '\''

        if idx < len(resources) - 1:
            sql += ' OR '

        if idx == len(resources) - 1:
            sql += ';'

    result = engine.execute(sql).fetchone()

    return result[0] or 0
