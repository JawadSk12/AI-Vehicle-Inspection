import sys
from pathlib import Path

_backend_dir = Path(__file__).resolve().parent.parent   # .../backend/
_project_root = _backend_dir.parent                     # .../Paint_defect/

for _p in (_backend_dir, _project_root):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from app.main import app

__all__ = ["app"]
