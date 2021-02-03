import psycopg2
import config
import sys

host = config.get_config('postgres.host')
port = config.get_config('postgres.port')
user = config.get_config('postgres.user')
password = config.get_config('postgres.password')
schema = config.get_config('postgres.schema')
database = config.get_config('postgres.database')

def __getCursor(databaseName):
    dsn = f"user='{user}' host='{host}' password='{password}' port='{port}'"
    if databaseName:
        dsn = f"{dsn} dbname={database}"

    try:
        connection = psycopg2.connect(dsn)

    except:
        print('No connection to database, exiting...')
        sys.exit(0)

    connection.autocommit = True
    return connection.cursor()


cur = __getCursor(None)
cur.execute("SELECT datname FROM pg_database;")
list_database = cur.fetchall()

if (database,) not in list_database:
    cur.execute(f"CREATE DATABASE {database};")
    cur = __getCursor(database)
    cur.execute('CREATE EXTENSION postgis;')
    print('Database created')

cur = __getCursor(database)

cur.execute(f"CREATE SCHEMA IF NOT EXISTS {schema}")

print('Database connected\n')

