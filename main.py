from psycopg2 import connect, extensions
import os
import sys
import django

connection = None
cursor = None
try:
    # connect to default database
    connection = connect(
        host='localhost',
        database='postgres',
        user='postgres',
        password='1793248650',
        port='5432',
    )

    cursor = connection.cursor()

    # auto commit the SQL queries
    auto_commit = extensions.ISOLATION_LEVEL_AUTOCOMMIT
    connection.set_isolation_level(auto_commit)

    # new database name
    database_name = input('Enter Database name: ')

    # check if the new database already exist
    cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{database_name}'")
    result = cursor.fetchone()

    # terminate all the sessions of existing database & drop it
    if result:
        cursor.execute(f"SELECT pg_terminate_backend(pg_stat_activity.pid) FROM pg_stat_activity WHERE pg_stat_activity.datname = '{database_name}'")
        cursor.execute(f"DROP DATABASE {database_name}")
        print(f"The database '{database_name}' has been dropped.")

    # create new database
    cursor.execute(f"CREATE DATABASE {database_name}")
    print(f"The database '{database_name}' has been created.")

    # change database name in settings.py
    print('------CHANGING DATABASE NAME IN SETTINGS.PY------')
    settings_file = 'Paralaxiom/settings.py'
    lines = []
    with open(settings_file, 'r') as f:
        lines = f.readlines()
    new_lines = []
    for line in lines:
        if 'NAME' in line:
            line = f"        'NAME': '{database_name}',\n"
        new_lines.append(line)
    with open(settings_file, 'w') as f:
        f.writelines(new_lines)

    # make migrations
    print('------RUNNING MIGRATIONS------')
    project_dir = os.path.join(os.path.dirname(__file__), '..', 'Paralaxiom')
    sys.path.append(project_dir)
    os.environ['DJANGO_SETTINGS_MODULE'] = 'Paralaxiom.settings'
    django.setup()
    os.system('python manage.py migrate')

except Exception as e:
    print(e)

finally:
    if cursor is not None:
        cursor.close()
    if connection is not None:
        connection.close()

