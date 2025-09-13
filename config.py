# config.py

from dotenv import load_dotenv
import os

load_dotenv()

# LLM API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
LLM_MODEL = "gemini"

# TTS 模型設定
TTS_MODEL = "bark"

# FFmpeg 設定
VIDEO_WIDTH = 1280
VIDEO_HEIGHT = 720
VIDEO_FPS = 30
OUTPUT_DIR = "assets/videos"
TEMP_DIR = "assets/audio"

# 背景圖路徑
DEFAULT_BG_IMAGE = "assets/images/bg_default.jpg"

# 字型路徑
FONT_PATH = "assets/fonts/NotoSansTC-Regular.ttf"
