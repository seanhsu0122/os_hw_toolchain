import os
import sys
import google.generativeai as genai
from google.api_core import exceptions

def generate_tts_audio(
    script: str, 
    output_path: str, 
    model: str = "models/tts-1"
):
    """
    使用 Gemini TTS API 生成音訊檔案。
    """
    try:
        print(f"腳本開始執行... 正在生成音訊，使用模型：{model}")
        
        # 呼叫 Gemini API 來合成語音
        response = genai.synthesize_speech(
            model=model,
            text=script,
        )

        # 將 API 回傳的二進位音訊內容寫入檔案
        with open(output_path, 'wb') as f:
            f.write(response.audio_content)

        print(f"音訊已成功生成並儲存至：{output_path}")

    except exceptions.GoogleAPICallError as e:
        print(f"API 呼叫失敗：{e}")
        print("請檢查您的 API 金鑰是否有效、帳戶是否啟用，或網路連線是否正常。")
    except Exception as e:
        print(f"發生未預期的錯誤：{e}")


# --- 程式執行的主入口 ---
if __name__ == "__main__":
    print(f"google-generativeai 套件版本: {genai.__version__}")
    
    # 1. 從環境變數讀取 API 金鑰
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("錯誤：環境變數 'GOOGLE_API_KEY' 未設定。請在執行時傳入。")
        sys.exit(1) # 結束程式

    # 2. 設定 SDK
    try:
        genai.configure(api_key=api_key)
        print("Gemini API 金鑰設定成功。")
    except Exception as e:
        print(f"設定 API 金鑰時發生錯誤: {e}")
        sys.exit(1)

    # 3. 定義要轉換的文字和輸出檔案路徑
    script_to_convert = "您好，這段語音是透過在 Colab 中執行 !python main.py 的方式生成的。"
    output_file_path = "tts_from_script.mp3"

    # 4. 呼叫函式
    generate_tts_audio(script_to_convert, output_file_path)
    
    print("腳本執行完畢。")