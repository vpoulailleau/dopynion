class InvalidCommandError(Exception):
    pass


class AddPlayerDuringGameError(InvalidCommandError):
    pass


class InvalidActionError(InvalidCommandError):
    pass


class ActionDuringBuyError(InvalidCommandError):
    pass


class MissingCardError(InvalidCommandError):
    pass


class InvalidBuyError(InvalidCommandError):
    pass


class NotEnoughMoneyError(InvalidCommandError):
    pass
