from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Paths:
    _BASE_DIR: Path = Path(__file__).resolve().parent
    _bot_photo_dir: Path = _BASE_DIR / "media" / "bot"

    welcome_photo = _bot_photo_dir / "welcome.jpg"


PATHS = Paths()