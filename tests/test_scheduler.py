import pytest
from src.core.scheduler import AgentScheduler

def test_scheduler_registers_all_jobs():
    scheduler = AgentScheduler()
    scheduler.setup()
    job_ids = [job.id for job in scheduler.scheduler.get_jobs()]
    assert "research_daily" in job_ids
    assert "strategy_weekly" in job_ids
    assert "analytics_daily" in job_ids
    assert "content_daily" in job_ids
    assert "social_daily" in job_ids
    assert "website_daily" in job_ids
    assert "post_production_daily" in job_ids

def test_scheduler_can_start_and_stop():
    scheduler = AgentScheduler()
    scheduler.start()
    assert scheduler.scheduler.running
    scheduler.stop()
    assert not scheduler.scheduler.running
