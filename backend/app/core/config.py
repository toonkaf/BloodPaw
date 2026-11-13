import os

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./dev.db")
JWT_SECRET = os.environ.get("JWT_SECRET", "dev-only-secret")
JWT_EXPIRE_MINUTES = int(os.environ.get("JWT_EXPIRE_MINUTES", "60"))
UPLOAD_DIR = os.environ.get("UPLOAD_DIR", "./uploads")
MAX_UPLOAD_BYTES = 2 * 1024 * 1024  # 2 MB
