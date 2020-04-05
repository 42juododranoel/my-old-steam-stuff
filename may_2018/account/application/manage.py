import sys
import argparse

from sqlalchemy_utils import create_database

from server import application, orm


def parse_args(args):
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('command')
    namespace = parser.parse_known_args(args)
    return namespace


def parse_database_args(args):
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--create', action='store_true')
    parser.add_argument('--create-tables', action='store_true')
    parser.add_argument('--drop-tables', action='store_true')
    namespace = parser.parse_args(args)
    return namespace


if __name__ == '__main__':
    application.app_context().push()
    args = sys.argv[1:]
    main_namespace, remaining_args = parse_args(args)

    if main_namespace.command == 'database':
        namespace = parse_database_args(remaining_args)

        if namespace.create:
            create_database(application.config['SQLALCHEMY_DATABASE_URI'])
        if namespace.drop_tables:
            orm.drop_all()
        if namespace.create_tables:
            orm.create_all()

    elif main_namespace.command == 'run':
        application.run(host='0.0.0.0')
