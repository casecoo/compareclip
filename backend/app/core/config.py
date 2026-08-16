import os
import sys
from pathlib import Path
from moviepy.config import change_settings

# Base directory paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
DEFAULT_AUDIO_PATH = BASE_DIR / "song.mp3"

def configure_imagemagick():
    """Configures ImageMagick path dynamically based on OS or Environment Variable."""
    env_binary = os.getenv("IMAGEMAGICK_BINARY")
    if env_binary and os.path.exists(env_binary):
        change_settings({"IMAGEMAGICK_BINARY": env_binary})
    elif sys.platform.startswith("win"):
        default_win_path = r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe"
        if os.path.exists(default_win_path):
            change_settings({"IMAGEMAGICK_BINARY": default_win_path})
        else:
            # Fallback to 'magick' executable if in PATH
            change_settings({"IMAGEMAGICK_BINARY": "magick"})
    else:
        # Linux / Docker standard path
        change_settings({"IMAGEMAGICK_BINARY": "/usr/bin/convert"})
