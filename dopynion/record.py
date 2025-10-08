import datetime
from pathlib import Path
from typing import Literal
from zoneinfo import ZoneInfo

from dopynion.data_model import (
    ActionRecord,
    Cards,
    ErrorRecord,
    Game,
    GameRecord,
    HookCallArgs,
    HookCallRecord,
    HookCallResult,
    HookResultRecord,
    PlayerTurnRecord,
)
from dopynion.player import Player

records_dir = Path.cwd() / "games"
records_dir.mkdir(parents=True, exist_ok=True)


class Record:
    def __init__(self) -> None:
        now = datetime.datetime.now(tz=ZoneInfo("Europe/Paris"))
        now_str = now.strftime("%Y_%m_%d__%H_%M_%S_%f")
        self._file = records_dir / f"game__{now_str}.dop"
        if self._file.exists():
            msg = f"game record is already created ({self._file})"
            raise ValueError(msg)
        self._file.write_text("", encoding="utf-8")
        self._game_record = GameRecord(date=now, stock=Cards())
        self.save(Game(finished=False, players=[], stock=Cards()))

    @staticmethod
    def load(path: Path) -> GameRecord:
        return GameRecord.model_validate_json(path.read_text(encoding="utf-8"))

    def save(self, game: Game) -> Path:
        for player in game.players:
            self._game_record.scores[player.name] = player.score
        self._file.write_text(self._game_record.model_dump_json(indent=None))
        return self._file

    def start_turn(self) -> None:
        self._game_record.turns.append(PlayerTurnRecord())

    def add_stock(self, stock: Cards) -> None:
        self._game_record.stock = stock

    def add_action(self, action: str, player: Player) -> None:
        turn = self._game_record.turns[-1]
        action_record = ActionRecord(
            action=action,
            player=player.state,
            score=player.score()["score"],
        )
        turn.actions.append(action_record)

    def add_error(self, error: str, player: Player) -> None:
        self._add_error(error, player, "error")

    def add_warning(self, error: str, player: Player) -> None:
        self._add_error(error, player, "warning")

    def _add_error(
        self,
        error: str,
        player: Player,
        type_: Literal["error", "warning"],
    ) -> None:
        if not self._game_record.turns:
            self._game_record.turns.append(PlayerTurnRecord())
        turn = self._game_record.turns[-1]
        error_record = ErrorRecord(error=error, player=player.state, type=type_)
        turn.actions.append(error_record)

    def add_hook_call(self, player: Player, name: str, args: HookCallArgs) -> None:
        turn = self._game_record.turns[-1]
        turn.actions.append(HookCallRecord(name=name, player=player.state, args=args))

    def add_hook_result(self, player: Player, result: HookCallResult) -> None:
        turn = self._game_record.turns[-1]
        turn.actions.append(HookResultRecord(player=player.state, result=result))
