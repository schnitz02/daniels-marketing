from fastapi import APIRouter
from src.core.ga4_client import GA4Client

router = APIRouter(prefix="/ga4", tags=["ga4"])
_ga4_client = GA4Client()


@router.get("/status")
def ga4_status():
    """Returns whether GA4 credentials are configured."""
    return _ga4_client.get_status()


@router.get("/seo")
def ga4_seo():
    """Returns organic search metrics for last 30 days. None if not connected."""
    return _ga4_client.get_seo_metrics()


@router.get("/sem")
def ga4_sem():
    """Returns paid search metrics for last 30 days. None if not connected."""
    return _ga4_client.get_sem_metrics()
