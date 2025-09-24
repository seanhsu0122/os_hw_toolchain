import gradio as gr
import os
import re
import time
from modules.script_generator import generate_script as sg_generate_script, generate_image_prompt, _initialize_llm as initialize_llm_model # 使用別名避免命名衝突
from modules.tts_module import generate_tts_audio
from modules.video_generator import generate_video as vg_generate_video # 使用別名避免命名衝突
from modules.image_generator import generate_background_image, initialize_image_model
from config import TEMP_DIR, DEFAULT_BG_IMAGE, VIDEO_WIDTH, VIDEO_HEIGHT

# --- Helper Functions ---

def sanitize_filename(text: str) -> str:
    """將字串清理成適合做為檔名的格式."""
    text = re.sub(r'[\\/*?:"<>|]', "", text)  # 移除無效字元
    text = re.sub(r'\s+', '_', text) # 將空白替換為底線
    return text[:50].strip('_')

# --- Backend Logic Functions (Originals, mostly unchanged) ---

def create_script(question, script_language):
    """Generates a script from a question."""
    if not question or not question.strip():
        raise gr.Error("問題不能為空！")
    try:
        print(f"[SCRIPT] 正在為 '{question[:30]}...' 生成演講稿...")
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
        timestamp = int(time.time())
        audio_filename = f"audio_{timestamp}.wav"
        audio_path = os.path.join(TEMP_DIR, audio_filename)
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

# --- State Management and UI Functions ---

def parse_and_load_questions(questions_text):
    """從輸入文字中解析問題並初始化任務狀態."""
    question_blocks = re.split(r'\n\s*\n', questions_text.strip())
    questions = []
    for block in question_blocks:
        if not block.strip(): continue
        question = ' '.join(line.strip() for line in block.split('\n'))
        question = re.sub(r"^\s*(\d+\.|\*|-)\s*", "", question).strip()
        if question: questions.append(question)
    
    if not questions:
        raise gr.Error("請輸入至少一個問題！")

    tasks_state = {q: {
        'script': '', 'audio_path': None, 'image_prompt': '',
        'bg_image_path': None, 'video_path': None
    } for q in questions}
    
    first_question = questions[0]
    return tasks_state, gr.update(choices=questions, value=first_question), *update_ui_for_selected_question(first_question, tasks_state)

def update_ui_for_selected_question(selected_question, tasks_state):
    """當使用者從下拉選單選擇不同問題時，更新 UI 介面."""
    if not selected_question or selected_question not in tasks_state:
        return "", None, "", None, None
    
    task_data = tasks_state.get(selected_question, {})
    return (
        task_data.get('script', ''),
        task_data.get('audio_path'),
        task_data.get('image_prompt', ''),
        task_data.get('bg_image_path'),
        task_data.get('video_path')
    )

# --- New Wrapper Functions for Single-Step Execution ---

def run_single_script_step(selected_question, tasks_state, script_language):
    """僅為當前選擇的任務生成演講稿。"""
    if not selected_question: raise gr.Error("請先選擇一個任務！")
    script = create_script(selected_question, script_language)
    tasks_state[selected_question]['script'] = script
    return tasks_state, script

def run_single_audio_step(selected_question, tasks_state, script_from_ui, tts_voice):
    """僅為當前選擇的任務生成語音。"""
    if not selected_question: raise gr.Error("請先選擇一個任務！")
    # 使用 UI 上可能已編輯過的腳本
    audio_path = create_audio(script_from_ui, tts_voice)
    tasks_state[selected_question]['audio_path'] = audio_path
    tasks_state[selected_question]['script'] = script_from_ui # 同步更新狀態
    return tasks_state, audio_path

def run_single_image_step(selected_question, tasks_state, script_from_ui, video_width, video_height):
    """僅為當前選擇的任務生成 AI 背景圖。"""
    if not selected_question: raise gr.Error("請先選擇一個任務！")
    image_prompt, image_path = create_background_image(selected_question, script_from_ui, video_width, video_height)
    tasks_state[selected_question]['image_prompt'] = image_prompt
    tasks_state[selected_question]['bg_image_path'] = image_path
    return tasks_state, image_prompt, image_path

def run_single_video_step(selected_question, tasks_state, background_image_upload, video_width, video_height, font_size, font_color, output_filename_prefix):
    """僅為當前選擇的任務合成影片。"""
    if not selected_question: raise gr.Error("請先選擇一個任務！")
    
    task_data = tasks_state[selected_question]
    audio_path = task_data.get('audio_path')
    # 優先使用任務自己的背景圖，若無則使用通用上傳的背景圖
    bg_path = task_data.get('bg_image_path') or background_image_upload

    if not audio_path: raise gr.Error("請先為此任務生成語音！")

    sanitized_q = sanitize_filename(selected_question)
    output_filename = f"{output_filename_prefix}_{sanitized_q}_single.mp4"
    
    video_path = create_video(audio_path, selected_question, selected_question, bg_path, video_width, video_height, font_size, font_color, output_filename)
    tasks_state[selected_question]['video_path'] = video_path
    return tasks_state, video_path

# --- Full Pipeline Functions ---

def run_single_pipeline_for_state(question, task_data, script_language, tts_voice, video_width, video_height, use_ai_image, background_image_upload, font_size, font_color, output_filename_prefix):
    """為單一問題執行完整的影片生成流程並更新其狀態 (供批次處理呼叫)。"""
    script = create_script(question, script_language)
    task_data['script'] = script
    audio_path = create_audio(script, tts_voice)
    task_data['audio_path'] = audio_path
    
    final_bg_path = background_image_upload
    if use_ai_image:
        image_prompt, final_bg_path = create_background_image(question, script, video_width, video_height)
        task_data['image_prompt'] = image_prompt
        task_data['bg_image_path'] = final_bg_path
    else:
        task_data['image_prompt'] = "未使用 AI 生成圖片"
        task_data['bg_image_path'] = final_bg_path
    
    sanitized_q = sanitize_filename(question)
    output_filename = f"{output_filename_prefix}_{sanitized_q}.mp4"
    video_path = create_video(audio_path, question, question, final_bg_path, video_width, video_height, font_size, font_color, output_filename)
    task_data['video_path'] = video_path
    return task_data

def process_all_tasks(tasks_state, script_language, tts_voice, video_width, video_height, use_ai_image, background_image_upload, font_size, font_color, output_filename_prefix, progress=gr.Progress(track_tqdm=True)):
    """為狀態中的所有任務執行整個影片生成流程."""
    if not tasks_state: raise gr.Error("沒有已載入的任務！請先輸入問題並點擊 '解析並載入問題'。")
    
    questions = list(tasks_state.keys())
    total_questions = len(questions)
    all_video_paths = []

    for i, question in enumerate(questions):
        progress(i / total_questions, desc=f"[{i+1}/{total_questions}] 處理中: {question[:30]}...")
        try:
            updated_task_data = run_single_pipeline_for_state(
                question, tasks_state[question], script_language, tts_voice, video_width, video_height,
                use_ai_image, background_image_upload, font_size, font_color, output_filename_prefix
            )
            tasks_state[question] = updated_task_data
            if updated_task_data.get('video_path'):
                all_video_paths.append(updated_task_data['video_path'])
        except Exception as e:
            gr.Warning(f"處理問題 '{question}' 時發生錯誤: {e}")
            continue
            
    progress(1.0, desc="全部處理完畢！")

    last_question = questions[-1]
    last_task_ui_updates = update_ui_for_selected_question(last_question, tasks_state)
    return tasks_state, all_video_paths, gr.update(value=last_question), *last_task_ui_updates

# --- Gradio UI ---
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    tasks_state = gr.State({})

    gr.Markdown("# 🔹 製作作業系統作業的系統作業程序 (多任務版)")
    
    with gr.Row():
        with gr.Column(scale=2):
            with gr.Group():
                gr.Markdown("### 0. 任務管理")
                question_input = gr.Textbox(label="請輸入所有問題 (以空白行分隔)", lines=10, placeholder="例如：\n1. CPU 和 GPU 的差別是什麼？\n\n2. 什麼是 RAM？")
                parse_questions_btn = gr.Button("解析並載入問題", variant="secondary")
                question_selector = gr.Dropdown(label="選擇要檢視/編輯的任務", interactive=True)

            with gr.Group():
                gr.Markdown("### 1. 演講稿 (Script)")
                script_language = gr.Dropdown(choices=["Traditional Chinese", "English", "Japanese"], value="Traditional Chinese", label="演講稿語言")
                script_output = gr.Textbox(label="生成的演講稿 (可編輯)", lines=8, interactive=True)
                generate_script_btn = gr.Button("僅生成此任務的演講稿", variant="secondary")

            with gr.Group():
                gr.Markdown("### 2. 語音 (Audio)")
                tts_voice = gr.Dropdown(choices=[("Zephyr", "Zephyr"), ("Puck", "Puck"), ("Charon", "Charon")], value="Zephyr", label="選擇語音人聲")
                audio_output = gr.Audio(label="生成的語音", type="filepath")
                generate_audio_btn = gr.Button("僅從上方演講稿生成語音", variant="secondary")

            with gr.Group():
                gr.Markdown("### 3. 影片 (Video)")
                with gr.Accordion("通用與單任務設定", open=True):
                    gr.Markdown("#### 背景圖片設定")
                    use_ai_image_for_all = gr.Checkbox(label="[執行所有任務時] 為每個任務生成新的 AI 背景", value=True)
                    background_image_upload = gr.Image(type="filepath", label="上傳通用背景 / AI 生成結果預覽")
                    generate_image_btn = gr.Button("僅為此任務生成 AI 背景 (會覆蓋上方)", variant="secondary")
                    image_prompt_output = gr.Textbox(label="AI 生成的圖片提示詞 (Prompt)", interactive=False)
                    
                    gr.Markdown("---")
                    gr.Markdown("#### 影片與字體設定")
                    output_filename_prefix = gr.Textbox(value="output", label="輸出檔名前綴")
                    with gr.Row():
                        video_width = gr.Slider(minimum=640, maximum=1920, value=VIDEO_WIDTH, step=2, label="影片寬度")
                        video_height = gr.Slider(minimum=360, maximum=1080, value=VIDEO_HEIGHT, step=2, label="影片高度")
                    with gr.Row():
                        font_size = gr.Slider(minimum=20, maximum=100, value=40, step=1, label="字體大小")
                        font_color = gr.ColorPicker(value="#ffffff", label="字體顏色")
                generate_video_btn = gr.Button("僅合成此任務的影片", variant="secondary")

        with gr.Column(scale=1):
            gr.Markdown("### 最終結果")
            output_video_preview = gr.Video(label="結果預覽 (當前選中或最後處理的任務)")
            output_files = gr.File(label="所有生成的影片檔案", file_count="multiple")
            process_all_btn = gr.Button("🚀 同時執行所有任務", variant="primary")

    # --- Event Listeners ---
    
    # 0. Load and parse questions
    parse_questions_btn.click(
        fn=parse_and_load_questions, inputs=[question_input],
        outputs=[tasks_state, question_selector, script_output, audio_output, image_prompt_output, background_image_upload, output_video_preview]
    )
    
    # Update UI when dropdown changes
    question_selector.change(
        fn=update_ui_for_selected_question, inputs=[question_selector, tasks_state],
        outputs=[script_output, audio_output, image_prompt_output, background_image_upload, output_video_preview]
    )
    
    # 1. Single Step: Generate Script
    generate_script_btn.click(
        fn=run_single_script_step, inputs=[question_selector, tasks_state, script_language],
        outputs=[tasks_state, script_output]
    )
    
    # 2. Single Step: Generate Audio
    generate_audio_btn.click(
        fn=run_single_audio_step, inputs=[question_selector, tasks_state, script_output, tts_voice],
        outputs=[tasks_state, audio_output]
    )

    # 3. Single Step: Generate Image
    generate_image_btn.click(
        fn=run_single_image_step, inputs=[question_selector, tasks_state, script_output, video_width, video_height],
        outputs=[tasks_state, image_prompt_output, background_image_upload]
    )

    # 4. Single Step: Generate Video
    generate_video_btn.click(
        fn=run_single_video_step, 
        inputs=[question_selector, tasks_state, background_image_upload, video_width, video_height, font_size, font_color, output_filename_prefix],
        outputs=[tasks_state, output_video_preview]
    )
    
    # Run All Pipeline
    process_all_btn.click(
        fn=process_all_tasks,
        inputs=[tasks_state, script_language, tts_voice, video_width, video_height, use_ai_image_for_all, background_image_upload, font_size, font_color, output_filename_prefix],
        outputs=[tasks_state, output_files, question_selector, script_output, audio_output, image_prompt_output, background_image_upload, output_video_preview]
    )

if __name__ == "__main__":
    print("正在預載入本地 LLM 模型，這可能需要幾分鐘時間...")
    initialize_llm_model()
    print("正在預載入圖片生成模型 (Stable Diffusion)，這可能需要幾分鐘時間...")
    initialize_image_model()
    print("所有模型預載入完成，啟動 Gradio 介面。")
    demo.launch(share=True)