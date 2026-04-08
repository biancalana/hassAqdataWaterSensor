import json
import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

DEFAULT_STATE_PATH = Path("state.json")


def load_state(path: Path = DEFAULT_STATE_PATH) -> dict | None:
    """Load state from JSON file. Returns None if file doesn't exist or is invalid."""
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except (json.JSONDecodeError, OSError) as e:
        logger.warning("Could not read state file: %s", e)
        return None


def save_state(
    path: Path,
    last_reading_date: str,
    last_reading_value: float,
    last_consumption: float,
) -> None:
    """Save state to JSON file."""
    state = {
        "last_reading_date": last_reading_date,
        "last_reading_value": last_reading_value,
        "last_consumption": last_consumption,
    }
    path.write_text(json.dumps(state, indent=2) + "\n")
    logger.info("State saved: %s", state)


def get_last_date(state: dict | None) -> datetime | None:
    """Extract last_reading_date from state as a datetime."""
    if not state or "last_reading_date" not in state:
        return None
    try:
        return datetime.strptime(state["last_reading_date"], "%Y-%m-%d")
    except ValueError:
        return None
