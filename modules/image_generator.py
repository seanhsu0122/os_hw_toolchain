import torch
from diffusers import DiffusionPipeline
import os
from config import IMAGE_DIR, VIDEO_WIDTH, VIDEO_HEIGHT

def generate_background_image(
    prompt: str, 
    output_name: str = "generated_bg.png",
    width: int = VIDEO_WIDTH,
    height: int = VIDEO_HEIGHT
):
    """
    使用 Stable Diffusion 生成背景圖片。

    Args:
        prompt (str): 用於生成圖片的文字提示。
        output_name (str, optional): 輸出的圖片檔名. Defaults to "generated_bg.png".
        width (int, optional): 圖片寬度. Defaults to VIDEO_WIDTH from config.
        height (int, optional): 圖片高度. Defaults to VIDEO_HEIGHT from config.

    Returns:
        str: 生成圖片的完整路徑。
    """
    try:
        # 檢查是否有可用的 GPU，否則使用 CPU。強烈建議在有 GPU 的環境下執行。
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"正在使用 {device} 進行圖片生成...")
        
        # 載入模型。第一次執行會需要下載模型檔案。
        # 使用 float16 可以節省 VRAM，加快生成速度。
        # 更換為較輕量的 SD 2.1 模型以節省 VRAM
        pipe = DiffusionPipeline.from_pretrained(
            "stabilityai/stable-diffusion-xl-base-1.0", 
            torch_dtype=torch.float16, 
            use_safetensors=True
        )
        
        # 啟用模型 CPU 卸載，大幅降低 VRAM 峰值使用量
        # 這會稍微降低生成速度，但在 VRAM 有限的環境下至關重要
        if device == "cuda":
            pipe.enable_model_cpu_offload()
        else:
            pipe = pipe.to(device)


        # 為了讓圖片更美觀，可以在提示詞中加入一些風格描述
        full_prompt = f"{prompt}, cinematic, beautiful, high-res, detailed, professional photography"
        negative_prompt = "out of frame, lowres, text, error, cropped, worst quality, low quality, jpeg artifacts, ugly, duplicate, morbid, mutilated, out of frame, extra fingers, mutated hands, poorly drawn hands, poorly drawn face, mutation, deformed, blurry, bad anatomy, bad proportions, extra limbs, cloned face, disfigured, gross proportions, malformed limbs, missing arms, missing legs, extra arms, extra legs, fused fingers, too many fingers, long neck, username, watermark, signature."
        
        # 生成圖片
        print(f"使用提示詞生成圖片: {full_prompt}")
        image = pipe(
            prompt=full_prompt, 
            negative_prompt=negative_prompt,
            width=width,
            height=height
        ).images[0]
        
        # 儲存圖片
        os.makedirs(IMAGE_DIR, exist_ok=True)
        output_path = os.path.join(IMAGE_DIR, output_name)
        image.save(output_path)
        
        print(f"圖片已成功生成並儲存至： {output_path}")
        return output_path

    except Exception as e:
        print(f"生成圖片時發生錯誤： {e}")
        raise

# --- 使用範例 ---
if __name__ == '__main__':
    # 執行此檔案可進行單獨測試
    if not torch.cuda.is_available():
        print("警告：未偵測到 CUDA GPU，將使用 CPU 生成，速度會非常慢。")
    test_prompt = "A quantum computer in a futuristic lab"
    generate_background_image(test_prompt)