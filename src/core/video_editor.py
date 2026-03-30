import os
import logging

logger = logging.getLogger(__name__)

class VideoEditor:
    WATERMARK_TEXT = "Daniel's Donuts"

    def add_branding(self, input_path: str, output_path: str) -> str:
        """Add branding watermark to a video. Falls back to file copy if moviepy unavailable."""
        try:
            from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
            clip = VideoFileClip(input_path)
            watermark = (
                TextClip(self.WATERMARK_TEXT, fontsize=36, color="white", font="Arial-Bold")
                .set_position(("center", "bottom"))
                .set_duration(clip.duration)
            )
            final = CompositeVideoClip([clip, watermark])
            final.write_videofile(output_path, codec="libx264", audio_codec="aac", logger=None)
            clip.close()
            final.close()
        except ImportError:
            import shutil
            shutil.copy(input_path, output_path)
            logger.warning("moviepy not available, copied file without branding: %s", output_path)
        except Exception as e:
            import shutil
            shutil.copy(input_path, output_path)
            logger.error("Video branding failed, copied raw: %s — %s", output_path, e)
        return output_path
