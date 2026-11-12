FROM python:3.12-slim AS base
WORKDIR /srv
COPY requirements.txt requirements-dev.txt ./

# ---- stage สำหรับรันเทส (Jenkins ใช้ --target test) ----
FROM base AS test
RUN pip install --no-cache-dir -r requirements-dev.txt
COPY . .
ENV DATABASE_URL=sqlite:// JWT_SECRET=test-secret
CMD ["pytest", "-q"]

# ---- stage สำหรับ production ----
FROM base AS runtime
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
