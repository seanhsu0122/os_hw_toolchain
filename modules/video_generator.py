# modules/video_generator.py
import os
import subprocess
from config import VIDEO_WIDTH, VIDEO_HEIGHT, VIDEO_FPS, OUTPUT_DIR, DEFAULT_BG_IMAGE, FONT_PATH

def generate_video(
    audio_path,
    question_text,
    output_name="output.mp4",
    bg_image_path=DEFAULT_BG_IMAGE,
    width=VIDEO_WIDTH,
    height=VIDEO_HEIGHT,
    font_size=40,
    font_color="black"
):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_path = os.path.join(OUTPUT_DIR, output_name)
    
    # FFmpeg 命令：背景 + 音訊 + 問題文字
    cmd = [
        "ffmpeg",
        "-y",  # Overwrite output file if it exists
        # "-loglevel", "error",
        "-loop", "1",
        "-i", bg_image_path,
        "-i", audio_path,
        "-vf", f"scale={width}:{height},drawtext=text='{question_text}':fontfile={FONT_PATH}:fontcolor={font_color}:fontsize={font_size}:x=10:y=10",
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
