import os
import google.generativeai as genai
from google.api_core import exceptions

def generate_tts_audio(
    script: str, 
    output_path: str, 
    model: str = "models/tts-1"
):
    """
    使用 Gemini TTS API 生成音訊檔案。

    Args:
        script (str): 要轉換為語音的文字腳本。
        output_path (str): 輸出音訊檔案的儲存路徑 (例如 'output.mp3')。
        model (str, optional): 要使用的 TTS 模型。
                                 'models/tts-1' -> 速度快，品質好
                                 'models/tts-1-hd' -> 品質更高，但生成速度較慢
                                 預設為 "models/tts-1"。
    """
    try:
        # Gemini TTS API 目前預設輸出為 MP3 格式
        # 未來 API 可能會支援更多格式
        if not output_path.lower().endswith('.mp3'):
            print("提醒：目前 Gemini TTS API 主要生成 MP3 格式，建議輸出檔案以 .mp3 結尾。")

        print(f"正在生成音訊，使用模型：{model}...")
        
        # 呼叫 Gemini API 來合成語音
        response = genai.synthesize_speech(
            model=model,
            text=script,
        )

        # 將 API 回傳的二進位音訊內容寫入檔案
        # 'wb' 表示以二進位寫入模式開啟檔案
        with open(output_path, 'wb') as f:
            f.write(response.audio_content)

        print(f"音訊已成功生成並儲存至：{output_path}")

    except exceptions.GoogleAPICallError as e:
        print(f"API 呼叫失敗：{e}")
        print("請檢查您的 API 金鑰是否有效、帳戶是否啟用，或網路連線是否正常。")
    except Exception as e:
        print(f"發生未預期的錯誤：{e}")