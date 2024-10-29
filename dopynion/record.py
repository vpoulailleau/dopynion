import datetime
from pathlib import Path

records_dir = Path.cwd() / "games"
records_dir.mkdir(parents=True, exist_ok=True)


class Record:
    def __init__(self) -> None:
        now = datetime.datetime.now(tz=datetime.UTC)
        now_str = now.strftime("%Y_%m_%d__%H_%M_%S")
        self._file = records_dir / f"game__{now_str}.dop"
        self._file.write_text("", encoding="utf-8")


record = Record()
