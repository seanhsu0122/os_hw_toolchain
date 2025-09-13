from google import genai
from google.genai import types
import wave
import os

def generate_tts_audio(
    script: str,
    output_path: str,
    model: str = "gemini-2.5-flash-preview-tts",
    voice_name: str = "Kore"
):
    """
    使用 Gemini TTS API 將文字腳本轉換為音訊檔案。

    Args:
        script (str): 要轉換為語音的文字腳本。
        output_path (str): 儲存生成之 WAV 音訊檔案的路徑。
        model (str, optional): 要使用的 TTS 模型。預設為 "gemini-2.5-flash-preview-tts"。
        voice_name (str, optional): 要使用的語音名稱。預設為 "Kore"。
    """
    try:
        # 初始化 Gemini 用戶端
        client = genai.Client()

        # 呼叫 API 以生成內容
        response = client.models.generate_content(
            model=model,
            contents=script,
            config=types.GenerateContentConfig(
                response_modalities=["AUDIO"],
                speech_config=types.SpeechConfig(
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(
                            voice_name=voice_name,  # 您可以根據需求更換其他人聲，例如 'Puck'
                        )
                    )
                ),
            )
        )

        # 從回應中提取音訊數據
        data = response.candidates[0].content.parts[0].inline_data.data

        # 將音訊數據寫入 WAV 檔案
        with wave.open(output_path, "wb") as wf:
            wf.setnchannels(1)  # 單聲道
            wf.setsampwidth(2)  # 16-bit PCM
            wf.setframerate(24000)  # 24kHz 取樣率
            wf.writeframes(data)

        print(f"音訊已成功生成並儲存至： {output_path}")

    except Exception as e:
        print(f"生成音訊時發生錯誤： {e}")

# --- 使用範例 ---
if __name__ == '__main__':
    # 請確認您已經設定好 GOOGLE_API_KEY 環境變數
    if "GOOGLE_API_KEY" not in os.environ:
        print("錯誤：請先設定 'GOOGLE_API_KEY' 環境變數。")
    else:
        text_to_speak = "Say cheerfully: Have a wonderful day!"
        output_file = "output_audio.wav"
        generate_tts_audio(text_to_speak, output_file)