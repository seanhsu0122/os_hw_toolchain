import gradio as gr
import os
import re
import time # 新增 time 模組
from modules.script_generator import generate_script as sg_generate_script, generate_image_prompt # 使用別名避免命名衝突
from modules.tts_module import generate_tts_audio
from modules.video_generator import generate_video as vg_generate_video # 使用別名避免命名衝突
from modules.image_generator import generate_background_image
from config import TEMP_DIR, DEFAULT_BG_IMAGE, VIDEO_WIDTH, VIDEO_HEIGHT

# --- Helper Functions ---

def sanitize_filename(text: str) -> str:
    """將字串清理成適合做為檔名的格式."""
    text = re.sub(r'[\\/*?:"<>|]', "", text)  # 移除無效字元
    text = re.sub(r'\s+', '_', text) # 將空白替換為底線
    return text[:50].strip('_')

# --- Backend Logic Functions ---

def create_script(question, script_language):
    """Generates a script from a question."""
    if not question or not question.strip():
        raise gr.Error("問題不能為空！")
    try:
        print("[SCRIPT] 正在生成演講稿...")
        script = sg_generate_script(question, language=script_language)
        print("[SCRIPT] 演講稿生成完畢。")
        return script
    except Exception as e:
        print(f"\n❌ [SCRIPT] 發生錯誤：{e}")
        raise gr.Error(f"生成演講稿時發生錯誤: {e}")

def create_audio(script, tts_voice):
    """Generates audio from a script."""
    if not script or not script.strip():
        raise gr.Error("演講稿不能為空！請先生成或輸入演講稿。")
    try:
        print("[AUDIO] 正在生成語音...")
        os.makedirs(TEMP_DIR, exist_ok=True)
        audio_path = os.path.join(TEMP_DIR, "generated_audio.wav") # 改為 .wav
        generate_tts_audio(script, audio_path, voice_name=tts_voice)
        print(f"[AUDIO] 語音生成完畢: {audio_path}")
        return audio_path
    except Exception as e:
        print(f"\n❌ [AUDIO] 發生錯誤：{e}")
        raise gr.Error(f"生成語音時發生錯誤: {e}")

def create_background_image(question, script, video_width, video_height):
    """Generates a background image from the script content."""
    if not script or not script.strip():
        raise gr.Error("演講稿不能為空，無法生成圖片！")
    if not question or not question.strip():
        raise gr.Error("問題不能為空，無法生成圖片！")
    try:
        print("[IMAGE] 正在為圖片生成建立提示詞...")
        image_prompt = generate_image_prompt(question, script)
        print(f"[IMAGE] 生成的圖片提示詞: '{image_prompt}'")

        print("[IMAGE] 正在使用提示詞生成背景圖片...")
        # 建立一個對檔案系統安全的檔名，使用時間戳以避免中文路徑
        timestamp = int(time.time())
        safe_filename = f"bg_{timestamp}.png"
        image_path = generate_background_image(
            image_prompt,
            output_name=safe_filename,
            width=int(video_width),
            height=int(video_height)
        )
        print(f"[IMAGE] 背景圖片生成完畢: {image_path}")
        return image_prompt, image_path
    except Exception as e:
        print(f"\n❌ [IMAGE] 發生錯誤：{e}")
        error_message = f"生成背景圖片時發生錯誤: {e}\n\n提示：圖片生成功能 (Stable Diffusion) 非常耗費資源，建議在有 NVIDIA GPU 的環境下執行。若使用 CPU 可能會非常緩慢或因記憶體不足而失敗。"
        raise gr.Error(error_message)

def create_video(audio_path, question, video_title, background_image, video_width, video_height, font_size, font_color, output_filename):
    """Generates a video from audio and other settings."""
    if not audio_path or not os.path.exists(audio_path):
        raise gr.Error("找不到音訊檔案！請先生成語音。")
    if not question and not video_title:
        raise gr.Error("影片標題或原始問題至少需要一個！")
    try:
        print("[VIDEO] 正在合成影片...")
        
        title_text = video_title if video_title and video_title.strip() else question
        bg_path = background_image if background_image and os.path.exists(background_image) else DEFAULT_BG_IMAGE

        # Convert rgba() color string from Gradio to FFmpeg-compatible hex format
        ffmpeg_font_color = font_color
        if isinstance(font_color, str) and font_color.startswith('rgba'):
            rgba_match = re.match(r"rgba\(([\d\.]+),\s*([\d\.]+),\s*([\d\.]+),\s*([\d\.]+)\)", font_color)
            if rgba_match:
                r, g, b, a = [float(c) for c in rgba_match.groups()]
                r_int, g_int, b_int = int(r), int(g), int(b)
                a_int = int(a * 255)
                ffmpeg_font_color = f"0x{r_int:02x}{g_int:02x}{b_int:02x}{a_int:02x}"

        video_path = vg_generate_video(
            audio_path=audio_path,
            question_text=title_text,
            output_name=output_filename,
            bg_image_path=bg_path,
            width=int(video_width),
            height=int(video_height),
            font_size=int(font_size),
            font_color=ffmpeg_font_color
        )
        
        print(f"\n✅ [VIDEO] 影片已成功生成：{video_path}")
        return video_path
    except Exception as e:
        print(f"\n❌ [VIDEO] 發生錯誤：{e}")
        raise gr.Error(f"合成影片時發生錯誤: {e}")

# --- Pipeline Orchestrator ---

def run_batch_pipeline(questions_text, script_language, tts_voice, video_width, video_height, use_ai_image, background_image_upload, video_title, font_size, font_color, output_filename_prefix, progress=gr.Progress(track_tqdm=True)):
    """為多個問題執行整個影片生成流程."""
    
    # 1. 從輸入文字中解析問題列表
    lines = questions_text.strip().split('\n')
    questions = [re.sub(r"^\d+\.\s*", "", line).strip() for line in lines if line.strip()]
    
    if not questions:
        raise gr.Error("請輸入至少一個問題！")

    video_paths = []
    total_questions = len(questions)
    
    # 用於儲存最後一個問題的結果以更新 UI 預覽
    last_script, last_audio, last_bg, last_video, last_prompt = "", None, None, None, ""

    for i, question in enumerate(questions):
        progress(i / total_questions, desc=f"[{i+1}/{total_questions}] 處理中: {question[:30]}...")
        
        try:
            # --- 為單一問題執行流程 ---
            
            # 步驟 1: 生成演講稿
            script = create_script(question, script_language)
            
            # 步驟 2: 生成語音
            audio_path = create_audio(script, tts_voice)
            
            # 步驟 3: 生成背景圖片
            final_bg_path = background_image_upload
            image_prompt_for_ui = "未使用 AI 生成圖片"
            if use_ai_image:
                image_prompt_for_ui, final_bg_path = create_background_image(question, script, video_width, video_height)
            
            # 步驟 4: 合成影片
            sanitized_q = sanitize_filename(question)
            unique_output_filename = f"{output_filename_prefix}_{sanitized_q}.mp4"
            
            current_video_title = video_title if video_title and video_title.strip() else question

            video_path = create_video(audio_path, question, current_video_title, final_bg_path, video_width, video_height, font_size, font_color, unique_output_filename)
            
            video_paths.append(video_path)

            # 更新最後一次的結果以供 UI 預覽
            last_script, last_audio, last_bg, last_video, last_prompt = script, audio_path, final_bg_path, video_path, image_prompt_for_ui

        except Exception as e:
            gr.Warning(f"處理問題 '{question}' 時發生錯誤: {e}")
            # 發生錯誤時，停止後續處理，但返回已成功生成的影片
            break

    progress(1.0, desc="全部處理完畢！")
    
    # 返回所有生成的影片路徑，以及最後一個的詳細資訊用於預覽
    return last_script, last_audio, last_bg, last_video, last_prompt, video_paths


# --- Gradio UI ---
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🔹 製作作業系統作業的系統作業程序")
    
    with gr.Row():
        with gr.Column(scale=2):
            # --- Section 1: Script ---
            with gr.Group():
                gr.Markdown("### 1. 演講稿 (Script)")
                question = gr.Textbox(
                    label="請輸入您的問題 (每行一個)", 
                    lines=10, 
                    placeholder="""例如：
1. CPU 和 GPU 的差別是什麼？
2. 什麼是 RAM？
什麼是量子糾纏？"""
                )
                script_language = gr.Dropdown(
                    choices=["Traditional Chinese", "English", "Japanese"], 
                    value="Traditional Chinese",
                    label="演講稿語言", 
                    allow_custom_value=True
                )
                generate_script_btn = gr.Button("生成演講稿", variant="secondary")
                script_output = gr.Textbox(label="生成的演講稿 (可編輯)", lines=8, interactive=True)

            # --- Section 2: Audio ---
            with gr.Group():
                gr.Markdown("### 2. 語音 (Audio)")
                tts_voice = gr.Dropdown(
                    # Choices are omitted for brevity, but they are the same as the original code
                    choices=[("Zephyr (Bright, Higher pitch)", "Zephyr"), ("Puck (Upbeat, Middle pitch)", "Puck"), ("Charon (Informative, Lower pitch)", "Charon")], #...and so on
                    value="Zephyr",
                    label="選擇語音人聲"
                )
                generate_audio_btn = gr.Button("從演講稿生成語音", variant="secondary")
                audio_output = gr.Audio(label="生成的語音", type="filepath")

            # --- Section 3: Video ---
            with gr.Group():
                gr.Markdown("### 3. 影片 (Video)")
                with gr.Accordion("影片設定", open=True):
                    video_title = gr.Textbox(label="影片標題文字", placeholder="留空則使用您的問題")
                    
                    gr.Markdown("#### 背景圖片設定")
                    use_ai_image_for_all = gr.Checkbox(label="[一鍵生成時] 使用 AI 生成新背景", value=True)
                    
                    background_image_input = gr.Image(type="filepath", label="上傳背景 / AI 生成結果預覽")
                    generate_image_btn = gr.Button("單獨生成 AI 背景圖 (會覆蓋上方圖片)", variant="secondary")
                    image_prompt_output = gr.Textbox(label="AI 生成的圖片提示詞 (Prompt)", interactive=False)
                    
                    gr.Markdown("---")
                    output_filename = gr.Textbox(value="output", label="輸出檔名前綴")
                    with gr.Row():
                        video_width = gr.Slider(minimum=640, maximum=1920, value=VIDEO_WIDTH, step=2, label="影片寬度")
                        video_height = gr.Slider(minimum=360, maximum=1080, value=VIDEO_HEIGHT, step=2, label="影片高度")
                    with gr.Row():
                        font_size = gr.Slider(minimum=20, maximum=100, value=40, step=1, label="字體大小")
                        font_color = gr.ColorPicker(value="#ffffff", label="字體顏色")
                generate_video_btn = gr.Button("合成影片", variant="secondary")

        with gr.Column(scale=1):
            gr.Markdown("### 最終結果")
            output_video = gr.Video(label="生成結果預覽 (最後一部)")
            output_files = gr.File(label="所有生成的影片檔案", file_count="multiple")
            run_all_btn = gr.Button("🚀 一鍵執行製作作業系統作業的系統作業程序", variant="primary")

    # --- Event Listeners ---
    
    # Individual step buttons
    generate_script_btn.click(
        fn=create_script,
        inputs=[question, script_language],
        outputs=[script_output]
    )
    
    generate_audio_btn.click(
        fn=create_audio,
        inputs=[script_output, tts_voice],
        outputs=[audio_output]
    )
    
    generate_image_btn.click(
        fn=create_background_image,
        inputs=[question, script_output, video_width, video_height],
        outputs=[image_prompt_output, background_image_input]
    )
    
    generate_video_btn.click(
        fn=create_video,
        inputs=[
            audio_output, question, video_title, background_image_input, 
            video_width, video_height, font_size, font_color, output_filename
        ],
        outputs=[output_video]
    )
    
    # "Run All" button
    run_all_btn.click(
        fn=run_batch_pipeline,
        inputs=[
            question, script_language, tts_voice, video_width, video_height, 
            use_ai_image_for_all, background_image_input, video_title, font_size, font_color, output_filename
        ],
        outputs=[script_output, audio_output, background_image_input, output_video, image_prompt_output, output_files]
    )

if __name__ == "__main__":
    demo.launch(share=True)