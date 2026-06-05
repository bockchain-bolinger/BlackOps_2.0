import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.core.config import get_secret


def test_get_secret_returns_none_for_missing():
    # Ensure it doesn't crash if secrets.json doesn't exist
    assert get_secret("NON_EXISTENT_KEY", "missing") is None
