import os
import logging
from collections import deque

from core.signals import ItemSignals
from core.database import transaction, Database

logging.basicConfig(
    filename=f'logs/{__name__}',
    level=logging.DEBUG
)


class BaseApplication:
    def __init__(self, verbosity=None, console=False):
        self.items = deque()
        self.database = Database('default')
        self.session = self.database.sessionmaker()

        self.logger = self.get_logger(__name__, verbosity, console)
        self.logger.debug('Application initialized')

    def get_logger(self, name=None, verbosity=None, console=False):
        logger = logging.getLogger(name or __name__)
        if console:
            logger.addHandler(logging.StreamHandler())
        if verbosity:
            logger.setLevel(getattr(logging, verbosity))
        return logger

    def add_items(self):
        pass

    def run_loop(self):
        while True:
            item = self.items[0]
            self.logger.debug(f'Picked {item}')

            try:
                action, args, kwargs = item.get_action()
            except StopIteration:
                self.logger.warning('No more actions')
                self.items.remove(item)
            else:
                self.logger.debug('Starting action')
                result = action(*args, **kwargs)

            if result in [ItemSignals.OK, ItemSignals.NEXT]:
                self.logger.debug('Signal OK/NEXT')
                self.items.rotate(-1)
            elif result == ItemSignals.DELETE:
                self.logger.debug('Signal DELETE')
                self.items.remove(item)

            self.logger.debug(f'Done {item}')
