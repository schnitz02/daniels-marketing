import logging
from dotenv import load_dotenv
load_dotenv()

import uvicorn
from src.db.database import init_db
from src.core.scheduler import AgentScheduler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_app():
    """Create and configure the FastAPI app with lifespan."""
    import os
    from contextlib import asynccontextmanager
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.staticfiles import StaticFiles

    _scheduler = AgentScheduler()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # Startup
        init_db()
        _scheduler.start()
        logger.info("Application started — http://127.0.0.1:8000")
        yield
        # Shutdown
        _scheduler.stop()

    app = FastAPI(title="Daniel's Donuts Marketing Agent", lifespan=lifespan)

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
        allow_credentials=True,
    )

    from src.api.routes import approvals, agents, dashboard
    from src.api.routes.social_stats import router as social_stats_router
    from src.api.routes.research import router as research_router
    from src.api.routes.social_analysis import router as social_analysis_router
    from src.api.routes.ga4 import router as ga4_router
    app.include_router(approvals.router, prefix="/api/approvals")
    app.include_router(agents.router, prefix="/api/agents")
    app.include_router(dashboard.router, prefix="/api/dashboard")
    app.include_router(social_stats_router, prefix="/api")
    app.include_router(research_router, prefix="/api")
    app.include_router(social_analysis_router, prefix="/api")
    app.include_router(ga4_router, prefix="/api")

    @app.get("/health")
    def health():
        return {"status": "ok", "service": "daniels-donuts-marketing"}

    return app


app = create_app()

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=False)
