from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Paths:
    _BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    _bot_photo_dir: Path = _BASE_DIR / "media" / "bot"
    user_photo_dir: Path = _BASE_DIR / "media" / "user"

    welcome_photo = _bot_photo_dir / "welcome.jpeg"

PATHS = Paths()
PATHS.user_photo_dir.mkdir(parents=True, exist_ok=True)
