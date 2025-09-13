import gradio as gr
import os
from google import genai
from modules.script_generator import generate_answer, answer_to_script
from modules.tts_module import generate_tts_audio
from modules.video_generator import generate_video
from config import TEMP_DIR, GEMINI_API_KEY, DEFAULT_BG_IMAGE, VIDEO_WIDTH, VIDEO_HEIGHT

# Configure Gemini API
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found. Please set it in your .env file.")
genai.configure(api_key=GEMINI_API_KEY)

def create_video_pipeline(
    question,
    script_language,
    tts_voice,
    video_width,
    video_height,
    background_image,
    video_title,
    font_size,
    font_color,
    output_filename
):
    """
    Orchestrates the entire video generation pipeline based on UI inputs.
    """
    try:
        # 確保暫存音訊的資料夾存在
        os.makedirs(TEMP_DIR, exist_ok=True)

        # --- Step 1 & 2: Generate Script ---
        print("步驟 1: 正在生成回答...")
        answer = generate_answer(question)
        print("步驟 2: 正在將回答轉換為演講稿...")
        script = answer_to_script(answer, question, language=script_language)
        
        # --- Step 3: Generate Audio ---
        print("步驟 3: 正在生成語音...")
        audio_path = os.path.join(TEMP_DIR, "generated_audio.mp3")
        generate_tts_audio(script, audio_path, voice_name=tts_voice)
        
        # --- Step 4: Generate Video ---
        print("步驟 4: 正在合成影片...")
        
        # 決定影片標題 (若使用者未輸入，則使用原始問題)
        title_text = video_title if video_title else question
        
        # 決定背景圖片 (若使用者未上傳，則使用預設圖片)
        bg_path = background_image if background_image else DEFAULT_BG_IMAGE

        video_path = generate_video(
            audio_path=audio_path,
            question_text=title_text,
            output_name=output_filename,
            bg_image_path=bg_path,
            width=int(video_width),
            height=int(video_height),
            font_size=int(font_size),
            font_color=font_color
        )
        
        print(f"\n✅ 影片已成功生成：{video_path}")
        return video_path

    except Exception as e:
        print(f"\n❌ 處理過程中發生錯誤：{e}")
        raise gr.Error(f"處理過程中發生錯誤: {e}")


# --- Gradio UI ---
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🔹 Q&A 自動影片生成系統")
    
    with gr.Row():
        with gr.Column(scale=1):
            question = gr.Textbox(label="請輸入您的問題", lines=3, placeholder="例如：什麼是量子糾纏？")
            
            with gr.Accordion("進階設定", open=False):
                script_language = gr.Dropdown(
                    choices=["Traditional Chinese", "English", "Japanese"], 
                    value="Traditional Chinese",
                    label="演講稿語言", 
                    allow_custom_value=True
                )
                tts_voice = gr.Dropdown(
                    choices=["Puck", "Kore", "Chitral", "Karli", "Lhotse"],
                    value="Puck",
                    label="選擇語音人聲"
                )
                video_title = gr.Textbox(label="影片標題文字", placeholder="留空則使用您的問題")
                output_filename = gr.Textbox(value="output.mp4", label="輸出檔名")
                
                with gr.Row():
                    video_width = gr.Slider(minimum=640, maximum=1920, value=VIDEO_WIDTH, step=2, label="影片寬度")
                    video_height = gr.Slider(minimum=360, maximum=1080, value=VIDEO_HEIGHT, step=2, label="影片高度")
                
                with gr.Row():
                    font_size = gr.Slider(minimum=20, maximum=100, value=40, step=1, label="字體大小")
                    font_color = gr.ColorPicker(value="#000000", label="字體顏色")

                background_image = gr.Image(type="filepath", label="上傳背景圖片 (預設為 config 中的圖片)")

            btn = gr.Button("開始生成影片", variant="primary")

        with gr.Column(scale=1):
            output_video = gr.Video(label="生成結果")

    btn.click(
        fn=create_video_pipeline,
        inputs=[
            question,
            script_language,
            tts_voice,
            video_width,
            video_height,
            background_image,
            video_title,
            font_size,
            font_color,
            output_filename
        ],
        outputs=output_video
    )

if __name__ == "__main__":
    demo.launch()