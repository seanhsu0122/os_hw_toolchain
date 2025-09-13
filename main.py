# main.py
import os
from modules.input_module import get_question
from modules.script_generator import generate_answer, answer_to_script
from modules.tts_module import generate_tts_audio
from modules.video_generator import generate_video
from config import TEMP_DIR

def main():
    question = get_question()
    answer = generate_answer(question)
    script = answer_to_script(answer)
    audio_path = os.path.join(TEMP_DIR, "generated_audio.wav")
    generate_tts_audio(script, audio_path)
    video_path = generate_video(audio_path, question)
    print(f"影片已生成：{video_path}")

if __name__ == "__main__":
    main()
