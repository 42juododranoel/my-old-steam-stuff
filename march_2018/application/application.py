from random import shuffle

from models import Screen
from steam.api import SteamAPI
from core.utils import import_settings
from providers.items import items
from core.application import BaseApplication

settings = import_settings()


class Application(BaseApplication):
    def add_items(self):
        self.logger.debug(f'Adding {len(items)} items')
        steam_api_key = settings.CREDENTIALS['steam']['api_key']
        steam_api_credentials = {
            'username': settings.CREDENTIALS['steam']['username'],
            'password': settings.CREDENTIALS['steam']['password'],
            'guard': settings.CREDENTIALS['steam']['guard'],
        }
        # TODO: Вынести в цикл for, если понадобится по акку на предмет
        steam_api = SteamAPI(steam_api_key, steam_api_credentials)
        shuffle(items)
        for item_info in items:
            item = Screen(
                item_info['item_nameid'],
                item_info['name'],
                steam_api,
                self
            )
            self.items.append(item)
