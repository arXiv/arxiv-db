import os
import secrets

db_url = os.environ.get('CLASSIC_DATABASE_URI', 'mysql+aiomysql://not-set-check-config.py/0000')  # arXiv legacy DB URL, must use aiomysql driver


allow_origins = [
    "https://dev.arxiv.org",
    "http://dev.arxiv.org:8001",
    "https://services.dev.arxiv.org",
    "http://services.dev.arxiv.org:8001",
    "https://api.beta.arxiv.org",
    "http://api.beta.arxiv.org:8001",
    "https://beta.arxiv.org",
    "https://arxiv.org",
    "http://localhost",
    "http://localhost:8000",
    "http://localhost:8001",
    "http://localhost:3000",
]

reload = bool(os.environ.get("RELOAD", False))
"""Sets uvicorn reloading on code changes, Do not use in produciton."""

uvicorn_debug = bool(os.environ.get("UVICORN_DEBUG", False))
"""Sets uvicorn debugging output, Avoid using in produciton."""

debug_logging = bool(os.environ.get("DEBUG_LOGGING", False))
"""Sets SQLAlchemy to echo debugging and sets log level to DEBUG for modapi"""

jwt_secret = os.environ.get("JWT_SECRET", "not-set-" + secrets.token_urlsafe(16))
"""NG JWT_SECRET from arxiv-auth login service.

Extra from urlsafe for when misconfigured."""


if bool(os.environ.get("DEBUG")):
    reload, uvicorn_debug, debug_logging = (True, True, True)
