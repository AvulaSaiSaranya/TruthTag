import atexit
import os
import sys
import tempfile
import uuid
from pathlib import Path

_project_root = Path(__file__).resolve().parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

os.environ["TRUTHTAG_ENV"] = "test"
os.environ["TRUTHTAG_JWT_SECRET"] = "test-only-secret-for-truthtag-api-tests-2026"
_test_db_path = Path(tempfile.gettempdir()) / f"truthtag-test-{uuid.uuid4().hex}.db"
os.environ["TRUTHTAG_DB_PATH"] = str(_test_db_path)


def _remove_test_database() -> None:
    for suffix in ("", "-wal", "-shm"):
        Path(f"{_test_db_path}{suffix}").unlink(missing_ok=True)


atexit.register(_remove_test_database)
