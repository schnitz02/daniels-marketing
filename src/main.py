import logging
from dotenv import load_dotenv
load_dotenv()

import uvicorn
from src.api.main import app
from src.core.scheduler import AgentScheduler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

scheduler = AgentScheduler()

@app.on_event("startup")
def start_scheduler():
    scheduler.start()
    logger.info("Application started")

@app.on_event("shutdown")
def stop_scheduler():
    scheduler.stop()

if __name__ == "__main__":
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=False)
