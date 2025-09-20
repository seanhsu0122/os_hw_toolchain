from bark import SAMPLE_RATE, generate_audio, preload_models
from scipy.io.wavfile import write as write_wav
import os

def generate_tts_audio(
    script: str,
    output_path: str,
    voice_name: str = "en_speaker_6"
):
    """
    使用 Bark TTS 將文字腳本轉換為音訊檔案。

    Args:
        script (str): 要轉換為語音的文字腳本。
        output_path (str): 儲存生成之 WAV 音訊檔案的路徑。
        voice_name (str, optional): Bark 的語音人聲預設。預設為 "en_speaker_6"。
    """
    try:
        # 載入模型到記憶體
        preload_models()

        print(f"正在使用 Bark (人聲: {voice_name}) 生成語音...")
        # 生成音訊
        audio_array = generate_audio(script, history_prompt=voice_name)

        # 將音訊數據寫入 WAV 檔案
        write_wav(output_path, SAMPLE_RATE, audio_array)

        print(f"音訊已成功生成並儲存至： {output_path}")

    except Exception as e:
        print(f"生成音訊時發生錯誤： {e}")
        raise

# --- 使用範例 ---
if __name__ == '__main__':
    text_to_speak = "Hello, this is a test of the local Bark TTS model."
    output_file = "output_audio.wav"
    generate_tts_audio(text_to_speak, output_file)