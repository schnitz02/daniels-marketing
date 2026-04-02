# tests/conftest.py
import pytest
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from src.db.models import Base
from src.db.database import get_db


@pytest.fixture(scope="function")
def db():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def _make_test_app(db_session):
    """Create a minimal FastAPI app for testing (no scheduler, in-memory DB)."""
    from fastapi.middleware.cors import CORSMiddleware
    from src.api.routes import approvals, agents, dashboard
    from src.api.routes.social_stats import router as social_stats_router
    from src.api.routes.research import router as research_router
    from src.api.routes.social_analysis import router as social_analysis_router

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        yield  # no scheduler, no real db init in tests

    app = FastAPI(lifespan=lifespan)
    app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
    app.include_router(approvals.router, prefix="/api/approvals")
    app.include_router(agents.router, prefix="/api/agents")
    app.include_router(dashboard.router, prefix="/api/dashboard")
    app.include_router(social_stats_router, prefix="/api")
    app.include_router(research_router, prefix="/api")
    app.include_router(social_analysis_router, prefix="/api")
    app.dependency_overrides[get_db] = lambda: db_session
    return app


@pytest.fixture(scope="function")
def client(db):
    app = _make_test_app(db)
    with TestClient(app) as c:
        yield c
