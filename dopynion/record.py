import datetime
from pathlib import Path

from dopynion.data_model import GameRecord

records_dir = Path.cwd() / "games"
records_dir.mkdir(parents=True, exist_ok=True)


class Record:
    def __init__(self) -> None:
        now = datetime.datetime.now(tz=datetime.UTC)
        now_str = now.strftime("%Y_%m_%d__%H_%M_%S")
        self._file = records_dir / f"game__{now_str}.dop"
        if self._file.exists():
            msg = "game record is already created"
            raise ValueError(msg)
        self._file.write_text("", encoding="utf-8")
        self._game_record = GameRecord(date=now)
        self.save()

    def save(self) -> None:
        self._file.write_text(self._game_record.model_dump_json(indent=4))


record = Record()
