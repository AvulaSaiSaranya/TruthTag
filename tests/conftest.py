"""Isolate API tests from local and production databases."""

import atexit
import os
import tempfile
import uuid
from pathlib import Path


os.environ["TRUTHTAG_ENV"] = "test"
os.environ["TRUTHTAG_JWT_SECRET"] = "test-only-secret-for-truthtag-api-tests-2026"
_test_db_path = Path(tempfile.gettempdir()) / f"truthtag-test-{uuid.uuid4().hex}.db"
os.environ["TRUTHTAG_DB_PATH"] = str(_test_db_path)


def _remove_test_database() -> None:
    for suffix in ("", "-wal", "-shm"):
        Path(f"{_test_db_path}{suffix}").unlink(missing_ok=True)


atexit.register(_remove_test_database)
