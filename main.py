# main.py
import os
from modules.input_module import get_question
from modules.script_generator import generate_answer, answer_to_script
from modules.tts_module import generate_tts_audio
from modules.video_generator import generate_video
from config import TEMP_DIR

def main():
    try:
        question = get_question()
        
        print("步驟 1: 正在生成回答...")
        answer = generate_answer(question)
        
        print("步驟 2: 正在將回答轉換為演講稿...")
        script = answer_to_script(answer)
        
        print("步驟 3: 正在生成語音 (此步驟可能需要較長時間)...")
        audio_path = os.path.join(TEMP_DIR, "generated_audio.wav")
        generate_tts_audio(script, audio_path)
        
        print("步驟 4: 正在合成影片...")
        video_path = generate_video(audio_path, question)
        
        print(f"\n✅ 影片已成功生成：{video_path}")
    except Exception as e:
        print(f"\n❌ 處理過程中發生錯誤：{e}")
        print("請檢查您的網路連線、API 金鑰或相關設定後再試一次。")

if __name__ == "__main__":
    main()
