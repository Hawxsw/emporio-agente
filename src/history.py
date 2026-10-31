import json

from src.config import HISTORY_DIR


def _file(session: str):
    return HISTORY_DIR / f"{session}.json"


def load_history(session: str) -> list[dict]:
    path = _file(session)
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def save_history(session: str, history: list[dict]) -> None:
    HISTORY_DIR.mkdir(exist_ok=True)
    _file(session).write_text(json.dumps(history, ensure_ascii=False, indent=2), encoding="utf-8")


def delete_history(session: str) -> None:
    _file(session).unlink(missing_ok=True)
