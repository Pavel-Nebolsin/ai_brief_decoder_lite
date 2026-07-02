from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.briefs import router as briefs_router

app = FastAPI(title="AI Brief Decoder Lite")
app.include_router(briefs_router)

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
