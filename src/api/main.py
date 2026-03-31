import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="Daniel's Donuts Marketing Agent")

# Serve generated media files (images, videos)
os.makedirs("./media", exist_ok=True)
app.mount("/media", StaticFiles(directory="./media"), name="media")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", "http://127.0.0.1:5173",
        "http://localhost:3000", "http://127.0.0.1:3000",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import routes after app creation to avoid circular imports
from src.api.routes import approvals, agents, dashboard  # noqa: E402
app.include_router(approvals.router, prefix="/api/approvals")
app.include_router(agents.router, prefix="/api/agents")
app.include_router(dashboard.router, prefix="/api/dashboard")
