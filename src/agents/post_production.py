import logging
from src.agents.base import BaseAgent
from src.agents.orchestrator import register_agent
from src.core.video_editor import VideoEditor
from src.db.models import Content

logger = logging.getLogger(__name__)

@register_agent("post_production")
class PostProductionAgent(BaseAgent):
    name = "post_production"

    async def run(self):
        pending_reels = self.db.query(Content).filter_by(type="reel", status="pending").all()
        editor = VideoEditor()
        processed = 0

        for content in pending_reels:
            branded_path = content.file_path.replace(".mp4", "_branded.mp4")
            try:
                editor.add_branding(content.file_path, branded_path)
                content.file_path = branded_path
                processed += 1
            except FileNotFoundError:
                logger.warning("PostProductionAgent: file not found, skipping: %s", content.file_path)
            except Exception as e:
                logger.error("PostProductionAgent: failed to process reel %d: %s", content.id, e)

        self.db.commit()
        return {"processed": processed}
