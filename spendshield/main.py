# main.py
import os
from dotenv import load_dotenv
# <-- adjust path if your .env lives somewhere else
load_dotenv(dotenv_path="/root/spendshieldfastapi/spendshield/app/.env")

import uuid
import logging

from fastapi import FastAPI, Request
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware
from starlette.middleware.gzip import GZipMiddleware
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

# ✅ Rate-limiting (SlowAPI)
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

# — your routers —
from app.api.v1.inventory             import router as inventory_router
# from app.api.v1.resource_snapshot     import router as snaps_router

# ========== Request-ID Middleware ==========
class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        rid = str(uuid.uuid4())
        request.state.request_id = rid
        logging.info(f"RID={rid} ▶ {request.method} {request.url}")
        response = await call_next(request)
        response.headers["X-Request-ID"] = rid
        logging.info(f"RID={rid} ◀ {response.status_code}")
        return response

# ========== App & Middleware ==========
app = FastAPI(title="SpendShield Demo", version="1.0.0")

# 1️⃣ Enforce HTTPS redirect
#app.add_middleware(HTTPSRedirectMiddleware)

# 2️⃣ GZip compress large responses
app.add_middleware(GZipMiddleware, minimum_size=1000)

# 3️⃣ CORS (allow all in demo; lock down in prod)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET","POST","PUT","DELETE"],
    allow_headers=["*"],
    allow_credentials=True,
)

# 4️⃣ Trusted Hosts (demo: localhost only)
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1"],
)

# 5️⃣ Rate-limiting: 10 requests per minute per IP
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(429, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# 6️⃣ Request-ID logging
app.add_middleware(RequestIDMiddleware)

# ========== Health-check ==========
@app.get("/health", tags=["health"])
def health():
    return {"status":"ok"}

# ========== Mount Routers (no auth) ==========
# Inventory endpoint: GET /app/v1/inventory/
app.include_router(
    inventory_router,
    prefix="/app/v1",
    tags=["inventory"],
)

# Snapshot CRUD endpoints: /app/v1/resource-snapshots/
# app.include_router(
#     snaps_router,
#     prefix="/app/v1",
#     tags=["snapshots"],
# )
