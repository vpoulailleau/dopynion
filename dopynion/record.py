import datetime
from pathlib import Path

from dopynion.data_model import ActionRecord, GameRecord, PlayerTurnRecord
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
        self._game_record = GameRecord(date=now)
        self.save()

    @staticmethod
    def load(path: Path) -> GameRecord:
        return GameRecord.model_validate_json(path.read_text(encoding="utf-8"))

    def save(self) -> None:
        self._file.write_text(self._game_record.model_dump_json(indent=None))

    def start_turn(self) -> None:
        self._game_record.turns.append(PlayerTurnRecord())

    def add_action(self, action: str, player: Player) -> None:
        turn = self._game_record.turns[-1]
        action_record = ActionRecord(
            action=action,
            player=player.state,
            score=player.score()["score"],
        )
        turn.actions.append(action_record)
