class AlphaStrategy:
    def __init__(self, screen, history):
        if history.stats['trend']

        self.screen = screen
        self.actions = (
            action for action in (
                (self.save, [], {}),
                (self.check, [], {}),
                (self.delete, [], {}),
            )
        )

    def initialize(self, history):
        pass

    def is_buying_profitable(self, price):
        pass

    def is_selling_profitable(self, price):
        pass
