# modules/video_generator.py
import os
import subprocess
from config import VIDEO_WIDTH, VIDEO_HEIGHT, VIDEO_FPS, OUTPUT_DIR, DEFAULT_BG_IMAGE

def generate_video(audio_path, question_text, output_name="output.mp4"):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_path = os.path.join(OUTPUT_DIR, output_name)
    
    # FFmpeg 命令：背景 + 音訊 + 問題文字
    cmd = [
        "ffmpeg",
        "-y",
        "-loop", "1",
        "-i", DEFAULT_BG_IMAGE,
        "-i", audio_path,
        "-vf", f"drawtext=text='{question_text}':fontcolor=white:fontsize=40:x=(w-text_w)/2:y=(h-text_h)/2",
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
