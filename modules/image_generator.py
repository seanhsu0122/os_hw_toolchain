import torch
from diffusers import DiffusionPipeline
import os
from config import IMAGE_DIR, VIDEO_WIDTH, VIDEO_HEIGHT

IMAGE_PIPE = None

def initialize_image_model():
    """
    初始化並載入 Stable Diffusion pipeline。
    此函數只會在第一次呼叫時實際載入模型。
    """
    global IMAGE_PIPE
    if IMAGE_PIPE is None:
        try:
            # 檢查是否有可用的 GPU，否則使用 CPU。強烈建議在有 GPU 的環境下執行。
            device = "cuda" if torch.cuda.is_available() else "cpu"
            print(f"首次載入 Stable Diffusion 模型，正在使用 {device}...")
            
            # 載入模型。第一次執行會需要下載模型檔案。
            pipe = DiffusionPipeline.from_pretrained(
                "stabilityai/stable-diffusion-xl-base-1.0", 
                torch_dtype=torch.float16,
                variant="fp16",
                use_safetensors=True
            )
            
            # 啟用模型 CPU 卸載，大幅降低 VRAM 峰值使用量
            if device == "cuda":
                pipe.enable_model_cpu_offload()
            else:
                pipe = pipe.to(device)
            
            IMAGE_PIPE = pipe
            print("Stable Diffusion 模型載入完成。")

        except Exception as e:
            print(f"載入 Stable Diffusion 模型時發生錯誤： {e}")
            raise

def generate_background_image(
    prompt: str, 
    output_name: str = "generated_bg.png",
    width: int = VIDEO_WIDTH,
    height: int = VIDEO_HEIGHT
):
    """
    使用已載入的 Stable Diffusion pipeline 生成背景圖片。

    Args:
        prompt (str): 用於生成圖片的文字提示。
        output_name (str, optional): 輸出的圖片檔名. Defaults to "generated_bg.png".
        width (int, optional): 圖片寬度. Defaults to VIDEO_WIDTH from config.
        height (int, optional): 圖片高度. Defaults to VIDEO_HEIGHT from config.

    Returns:
        str: 生成圖片的完整路徑。
    """
    # 確保模型已初始化
    initialize_image_model()
    
    try:
        # 為了讓圖片更美觀，可以在提示詞中加入一些風格描述
        full_prompt = f"{prompt}, cinematic, beautiful, high-res, detailed, professional photography"
        negative_prompt = "out of frame, lowres, text, error, cropped, worst quality, low quality, jpeg artifacts, ugly, duplicate, morbid, mutilated, out of frame, extra fingers, mutated hands, poorly drawn hands, poorly drawn face, mutation, deformed, blurry, bad anatomy, bad proportions, extra limbs, cloned face"

        # 生成圖片
        image = IMAGE_PIPE(
            full_prompt, 
            negative_prompt=negative_prompt,
            width=width, 
            height=height,
            num_inference_steps=30,
            guidance_scale=7.5
        ).images[0]

        # 儲存圖片
        os.makedirs(IMAGE_DIR, exist_ok=True)
        output_path = os.path.join(IMAGE_DIR, output_name)
        image.save(output_path)
        print(f"背景圖片已生成： {output_path}")

        return output_path

    except Exception as e:
        print(f"生成背景圖片時發生錯誤： {e}")
        raise