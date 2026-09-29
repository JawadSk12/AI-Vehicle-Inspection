import sys
from pathlib import Path
_b = Path(__file__).resolve().parent.parent
if str(_b) not in sys.path:
    sys.path.insert(0, str(_b))

from app.routes import auth, dashboard, inspections, predict, reports

__all__ = ["auth", "dashboard", "inspections", "predict", "reports"]
