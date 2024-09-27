class InvalidCommandError(Exception):
    pass


class AddPlayerDuringGameError(InvalidCommandError):
    pass


class InvalidActionError(Exception):
    pass


class UnknownActionError(Exception):
    pass
