from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.briefs import router as briefs_router
from app.repositories import PersistenceError

app = FastAPI(title="AI Brief Decoder Lite")
app.include_router(briefs_router)


@app.exception_handler(PersistenceError)
async def persistence_error_handler(request: Request, exc: PersistenceError) -> JSONResponse:
    """Map database failures to HTTP 500 with a generic message — an infrastructure
    failure, unlike domain-level decode failures which stay within "always 200"."""
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})

# A regex is required (not a static origin list) because each unpacked/installed
# extension gets a different chrome-extension:// id, which isn't known in advance.
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"chrome-extension://.*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
