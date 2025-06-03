import datetime
from pathlib import Path

from dopynion.data_model import (
    ActionRecord,
    Cards,
    ErrorRecord,
    Game,
    GameRecord,
    PlayerTurnRecord,
)
from dopynion.player import Player

records_dir = Path.cwd() / "games"
records_dir.mkdir(parents=True, exist_ok=True)


class Record:
    def __init__(self) -> None:
        now = datetime.datetime.now(tz=datetime.UTC)
        now_str = now.strftime("%Y_%m_%d__%H_%M_%S")
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
        if not self._game_record.turns:
            self._game_record.turns.append(PlayerTurnRecord())
        turn = self._game_record.turns[-1]
        error_record = ErrorRecord(
            error=error,
            player=player.state,
        )
        turn.actions.append(error_record)
