import os
import numpy as np
from scipy.io.wavfile import write as write_wav
import torch

# 修正 PyTorch 2.6+ 與 bark 的載入問題
# 必須在 import bark 之前執行
# 根據錯誤訊息提示，加入此行以允許載入必要的 numpy 型別
torch.serialization.add_safe_globals([np.core.multiarray.scalar])

from bark import generate_audio, SAMPLE_RATE

def generate_tts_audio(script: str, output_path: str):
    """
    將文字腳本轉換為語音並儲存為 WAV 檔案。

    :param script: 待轉換的文字腳本。
    :param output_path: 輸出的音訊檔案路徑。
    """
    # 生成語音
    audio_array = generate_audio(script, history_prompt="en_speaker_6")
    
    # 確保父目錄存在
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # 將語音寫入 WAV 檔案
    write_wav(output_path, SAMPLE_RATE, audio_array.astype(np.float32))
    print(f"成功產生語音檔案: {output_path}")


if __name__ == "__main__":
    # 測試腳本
    print("--- 執行語音生成測試 ---")
    
    # 使用一個範例腳本進行測試
    sample_script = "大家好，這是一個測試語音。我們將這個文字轉換成一段語音檔案，並儲存在 videos 資料夾中。"
    output_dir = "videos"
    output_filename = "test_audio.wav"
    output_path = os.path.join(output_dir, output_filename)
    
    try:
        generate_tts_audio(sample_script, output_path)
    except Exception as e:
        print(f"執行過程中發生錯誤：{e}")
        print("請確認已安裝 bark 函式庫。")
