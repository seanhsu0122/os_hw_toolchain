# modules/video_generator.py
import os
import subprocess
import textwrap
from config import VIDEO_WIDTH, VIDEO_HEIGHT, VIDEO_FPS, OUTPUT_DIR, DEFAULT_BG_IMAGE, FONT_PATH

def generate_video(
    audio_path,
    question_text,
    output_name="output.mp4",
    bg_image_path=DEFAULT_BG_IMAGE,
    width=VIDEO_WIDTH,
    height=VIDEO_HEIGHT,
    font_size=40,
    font_color="white"
):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_path = os.path.join(OUTPUT_DIR, output_name)
    
    # 根據影片寬度和字體大小估算每行字數，以進行自動換行
    # 這是一個估算值，假設平均字元寬度約為字體大小的 0.7 倍
    # 並在影片左右留下一些邊界 (95%)
    chars_per_line = max(10, int((width * 0.95) / (font_size * 0.7)))
    wrapped_text = textwrap.fill(question_text, width=chars_per_line)
    
    # 為了 ffmpeg 的 drawtext 濾鏡，需要逸出特殊字元
    escaped_text = wrapped_text.replace("'", r"\'").replace(":", r"\:")
    
    # FFmpeg 命令：背景 + 音訊 + 問題文字
    cmd = [
        "ffmpeg",
        "-y",  # Overwrite output file if it exists
        # "-loglevel", "error",
        "-loop", "1",
        "-i", bg_image_path,
        "-i", audio_path,
        "-vf", f"scale={width}:{height},drawtext=text='{escaped_text}':fontfile={FONT_PATH}:fontcolor={font_color}:fontsize={font_size}:x=(w-text_w)/2:y=50:box=1:boxcolor=black@0.5:boxborderw=15",
        "-c:v", "libx264",
        "-tune", "stillimage",
        "-c:a", "aac",
        "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        "-shortest",
        output_path
    ]
    subprocess.run(cmd, check=True)
    return output_path
