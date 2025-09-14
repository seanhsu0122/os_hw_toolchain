import gradio as gr
import os
import re
from modules.script_generator import generate_script
from modules.tts_module import generate_tts_audio
from modules.video_generator import generate_video
from config import TEMP_DIR, DEFAULT_BG_IMAGE, VIDEO_WIDTH, VIDEO_HEIGHT

# --- Backend Functions for each step ---

def step1_generate_script(question, script_language):
    """Generates a script from a question."""
    if not question or not question.strip():
        raise gr.Error("問題不能為空！")
    try:
        print("步驟 1: 正在生成演講稿...")
        script = generate_script(question, language=script_language)
        return script
    except Exception as e:
        print(f"\n❌ 步驟 1 發生錯誤：{e}")
        raise gr.Error(f"生成演講稿時發生錯誤: {e}")

def step2_generate_audio(script, tts_voice):
    """Generates audio from a script."""
    if not script or not script.strip():
        raise gr.Error("演講稿不能為空！請先生成或輸入演講稿。")
    try:
        print("步驟 2: 正在生成語音...")
        os.makedirs(TEMP_DIR, exist_ok=True)
        audio_path = os.path.join(TEMP_DIR, "generated_audio.mp3")
        generate_tts_audio(script, audio_path, voice_name=tts_voice)
        return audio_path
    except Exception as e:
        print(f"\n❌ 步驟 2 發生錯誤：{e}")
        raise gr.Error(f"生成語音時發生錯誤: {e}")

def step3_generate_video(audio_path, question, video_title, background_image, video_width, video_height, font_size, font_color, output_filename):
    """Generates a video from audio and other settings."""
    if not audio_path or not os.path.exists(audio_path):
        raise gr.Error("找不到音訊檔案！請先生成語音。")
    if not question and not video_title:
        raise gr.Error("影片標題或原始問題至少需要一個！")
    try:
        print("步驟 3: 正在合成影片...")
        
        title_text = video_title if video_title else question
        bg_path = background_image if background_image else DEFAULT_BG_IMAGE

        # Convert rgba() color string from Gradio to FFmpeg-compatible hex format
        ffmpeg_font_color = font_color
        if isinstance(font_color, str) and font_color.startswith('rgba'):
            rgba_match = re.match(r"rgba\(([\d\.]+),\s*([\d\.]+),\s*([\d\.]+),\s*([\d\.]+)\)", font_color)
            if rgba_match:
                r, g, b, a = [float(c) for c in rgba_match.groups()]
                r_int, g_int, b_int = int(r), int(g), int(b)
                a_int = int(a * 255)
                ffmpeg_font_color = f"0x{r_int:02x}{g_int:02x}{b_int:02x}{a_int:02x}"

        video_path = generate_video(
            audio_path=audio_path,
            question_text=title_text,
            output_name=output_filename,
            bg_image_path=bg_path,
            width=int(video_width),
            height=int(video_height),
            font_size=int(font_size),
            font_color=ffmpeg_font_color
        )
        
        print(f"\n✅ 影片已成功生成：{video_path}")
        return video_path
    except Exception as e:
        print(f"\n❌ 步驟 3 發生錯誤：{e}")
        raise gr.Error(f"合成影片時發生錯誤: {e}")

def run_full_pipeline(question, script_language, tts_voice, video_width, video_height, background_image, video_title, font_size, font_color, output_filename):
    """Orchestrates the entire video generation pipeline."""
    script = step1_generate_script(question, script_language)
    audio_path = step2_generate_audio(script, tts_voice)
    video_path = step3_generate_video(audio_path, question, video_title, background_image, video_width, video_height, font_size, font_color, output_filename)
    return script, audio_path, video_path


# --- Gradio UI ---
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🔹 Q&A 自動影片生成系統")
    
    with gr.Row():
        with gr.Column(scale=2):
            # --- Step 1: Script Generation ---
            with gr.Group():
                gr.Markdown("### 步驟 1: 生成演講稿")
                question = gr.Textbox(label="請輸入您的問題", lines=3, placeholder="例如：什麼是量子糾纏？")
                script_language = gr.Dropdown(
                    choices=["Traditional Chinese", "English", "Japanese"], 
                    value="Traditional Chinese",
                    label="演講稿語言", 
                    allow_custom_value=True
                )
                generate_script_btn = gr.Button("1. 生成演講稿", variant="secondary")
                script_output = gr.Textbox(label="生成的演講稿 (可編輯)", lines=8, interactive=True)

            # --- Step 2: Audio Generation ---
            with gr.Group():
                gr.Markdown("### 步驟 2: 生成語音")
                tts_voice = gr.Dropdown(
                    choices=[
                        ("Zephyr (Bright, Higher pitch)", "Zephyr"),
                        ("Puck (Upbeat, Middle pitch)", "Puck"),
                        ("Charon (Informative, Lower pitch)", "Charon"),
                        ("Kore (Firm, Middle pitch)", "Kore"),
                        ("Fenrir (Excitable, Lower middle pitch)", "Fenrir"),
                        ("Leda (Youthful, Higher pitch)", "Leda"),
                        ("Orus (Firm, Lower middle pitch)", "Orus"),
                        ("Aoede (Breezy, Middle pitch)", "Aoede"),
                        ("Callirrhoe (Easy-going, Middle pitch)", "Callirrhoe"),
                        ("Autonoe (Bright, Middle pitch)", "Autonoe"),
                        ("Enceladus (Breathy, Lower pitch)", "Enceladus"),
                        ("Iapetus (Clear, Lower middle pitch)", "Iapetus"),
                        ("Umbriel (Easy-going, Lower middle pitch)", "Umbriel"),
                        ("Algieba (Smooth, Lower pitch)", "Algieba"),
                        ("Despina (Smooth, Middle pitch)", "Despina"),
                        ("Erinome (Clear, Middle pitch)", "Erinome"),
                        ("Algenib (Gravelly, Lower pitch)", "Algenib"),
                        ("Rasalgethi (Informative, Middle pitch)", "Rasalgethi"),
                        ("Laomedeia (Upbeat, Higher pitch)", "Laomedeia"),
                        ("Achernar (Soft, Higher pitch)", "Achernar"),
                        ("Alnilam (Firm, Lower middle pitch)", "Alnilam"),
                        ("Schedar (Even, Lower middle pitch)", "Schedar"),
                        ("Gacrux (Mature, Middle pitch)", "Gacrux"),
                        ("Pulcherrima (Forward, Middle pitch)", "Pulcherrima"),
                        ("Achird (Friendly, Lower middle pitch)", "Achird"),
                        ("Zubenelgenubi (Casual, Lower middle pitch)", "Zubenelgenubi"),
                        ("Vindemiatrix (Gentle, Middle pitch)", "Vindemiatrix"),
                        ("Sadachbia (Lively, Lower pitch)", "Sadachbia"),
                        ("Sadaltager (Knowledgeable, Middle pitch)", "Sadaltager"),
                        ("Sulafat (Warm, Middle pitch)", "Sulafat")
                    ],
                    value="Zephyr",
                    label="選擇語音人聲"
                )
                generate_audio_btn = gr.Button("2. 從演講稿生成語音", variant="secondary")
                audio_output = gr.Audio(label="生成的語音", type="filepath")

            # --- Step 3: Video Generation ---
            with gr.Group():
                gr.Markdown("### 步驟 3: 合成影片")
                with gr.Accordion("影片設定", open=True):
                    video_title = gr.Textbox(label="影片標題文字", placeholder="留空則使用您的問題")
                    background_image = gr.Image(type="filepath", label="上傳背景圖片 (預設為 config 中的圖片)")
                    output_filename = gr.Textbox(value="output.mp4", label="輸出檔名")
                    with gr.Row():
                        video_width = gr.Slider(minimum=640, maximum=1920, value=VIDEO_WIDTH, step=2, label="影片寬度")
                        video_height = gr.Slider(minimum=360, maximum=1080, value=VIDEO_HEIGHT, step=2, label="影片高度")
                    with gr.Row():
                        font_size = gr.Slider(minimum=20, maximum=100, value=40, step=1, label="字體大小")
                        font_color = gr.ColorPicker(value="#000000", label="字體顏色")
                generate_video_btn = gr.Button("3. 合成影片", variant="secondary")

        with gr.Column(scale=1):
            gr.Markdown("### 最終結果")
            output_video = gr.Video(label="生成結果")
            run_all_btn = gr.Button("🚀 一鍵生成全部", variant="primary")

    # --- Event Listeners ---
    
    # Individual step buttons
    generate_script_btn.click(
        fn=step1_generate_script,
        inputs=[question, script_language],
        outputs=[script_output]
    )
    
    generate_audio_btn.click(
        fn=step2_generate_audio,
        inputs=[script_output, tts_voice],
        outputs=[audio_output]
    )
    
    generate_video_btn.click(
        fn=step3_generate_video,
        inputs=[
            audio_output, question, video_title, background_image, 
            video_width, video_height, font_size, font_color, output_filename
        ],
        outputs=[output_video]
    )
    
    # "Run All" button
    run_all_btn.click(
        fn=run_full_pipeline,
        inputs=[
            question, script_language, tts_voice, video_width, video_height, 
            background_image, video_title, font_size, font_color, output_filename
        ],
        outputs=[script_output, audio_output, output_video]
    )

if __name__ == "__main__":
    demo.launch()