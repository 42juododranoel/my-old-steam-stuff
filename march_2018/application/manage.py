import os

from steam.api import SteamAPI


if __name__ == '__main__':
    os.environ.setdefault('HAKUREI_SETTINGS_MODULE', 'settings')

    from application import Application
    application = Application(verbosity='DEBUG', console=True)

    if application.database.is_present:
        application.database.drop()

    application.database.create()
    application.database.create_tables()

    application.add_items()
    application.run_loop()
