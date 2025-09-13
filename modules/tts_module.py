import os
from scipy.io.wavfile import write as write_wav
from transformers import AutoProcessor, BarkModel
import torch

# --- 模型初始化 ---
# 載入模型和處理器。這會在模組首次匯入時執行一次，避免重複載入。
print("正在載入 Bark TTS 模型，第一次執行可能需要下載模型檔案...")
processor = AutoProcessor.from_pretrained("suno/bark")
model = BarkModel.from_pretrained("suno/bark")

# 檢查是否有可用的 GPU，並將模型移至對應裝置
device = "cuda:0" if torch.cuda.is_available() else "cpu"
model = model.to(device)
print(f"Bark 模型已載入並使用 {device} 裝置。")
# --- 模型初始化結束 ---

def generate_tts_audio(script: str, output_path: str):
    """
    將文字腳本轉換為語音並儲存為 WAV 檔案。
    使用 Hugging Face transformers 的 suno/bark 模型。

    :param script: 待轉換的文字腳本。
    :param output_path: 輸出的音訊檔案路徑。
    """
    # 雖然 bark 支援多語言，但特定 voice_preset 可能會影響中文發音，en_speaker_6 是個泛用選項
    voice_preset = "v2/en_speaker_6"
    
    inputs = processor(script, voice_preset=voice_preset, return_tensors="pt").to(device)
    
    # 生成語音
    # 使用 torch.inference_mode() 可以在不計算梯度的情況下執行，以提高效能
    with torch.inference_mode():
        # 增加一些生成參數以提高穩定性
        audio_array = model.generate(**inputs, pad_token_id=processor.tokenizer.pad_token_id)
    
    audio_array = audio_array.cpu().numpy().squeeze()
    
    sample_rate = model.generation_config.sample_rate
    
    # 確保父目錄存在
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # 將語音寫入 WAV 檔案
    # transformers 輸出的 numpy array 通常是 float32，可以直接寫入
    write_wav(output_path, sample_rate, audio_array)
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
        print("請確認已安裝 transformers, torch, accelerate 函式庫。")
