from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from dopynion.player import Player


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


class InvalidDiscardError(InvalidCommandError):
    pass


class HookError(InvalidCommandError):
    def __init__(
        self,
        player: "Player",
        *args: tuple[Any],
        **kwargs: dict[str, Any],
    ) -> None:
        super().__init__(*args, **kwargs)
        self.player = player
