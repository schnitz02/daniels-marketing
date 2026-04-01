import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

logger = logging.getLogger(__name__)

class AgentScheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler()

    def setup(self):
        self.scheduler.add_job(self._make_job("research"), CronTrigger(hour=6), id="research_daily", replace_existing=True)
        self.scheduler.add_job(self._make_job("analytics"), CronTrigger(hour=20), id="analytics_daily", replace_existing=True)
        self.scheduler.add_job(self._make_job("strategy"), CronTrigger(day_of_week="mon", hour=7), id="strategy_weekly", replace_existing=True)
        self.scheduler.add_job(self._make_job("content"), CronTrigger(hour=9), id="content_daily", replace_existing=True)
        self.scheduler.add_job(self._make_job("post_production"), CronTrigger(hour=10), id="post_production_daily", replace_existing=True)
        self.scheduler.add_job(self._make_job("social"), CronTrigger(hour=11), id="social_daily", replace_existing=True)
        self.scheduler.add_job(self._make_job("social_stats"), CronTrigger(hour=9, minute=30), id="social_stats_daily", replace_existing=True)
        self.scheduler.add_job(self._make_job("website"), CronTrigger(hour=12), id="website_daily", replace_existing=True)

    def _make_job(self, agent_name: str):
        def job():
            from src.db.database import SessionLocal
            # Import all agent modules to populate the registry
            import src.agents.research  # noqa
            import src.agents.strategy  # noqa
            import src.agents.content   # noqa
            import src.agents.post_production  # noqa
            import src.agents.social    # noqa
            import src.agents.website   # noqa
            import src.agents.analytics # noqa
            import src.agents.social_stats  # noqa
            from src.agents.orchestrator import OrchestratorAgent
            import asyncio
            db = SessionLocal()
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    loop.run_until_complete(OrchestratorAgent(db=db).trigger_agent(agent_name))
                finally:
                    loop.close()
            except Exception as e:
                logger.error("Scheduler: agent %s failed: %s", agent_name, e)
            finally:
                db.close()
        job.__name__ = f"job_{agent_name}"
        return job

    def start(self):
        self.setup()
        self.scheduler.start()
        logger.info("AgentScheduler started")

    def stop(self):
        self.scheduler.shutdown(wait=False)
        logger.info("AgentScheduler stopped")
