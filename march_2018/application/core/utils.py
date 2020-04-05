import os


def import_module(parent, name):
    return __import__(parent + '.' + name, fromlist=[name])


def import_settings():
    return __import__(os.environ.get('HAKUREI_SETTINGS_MODULE'))
