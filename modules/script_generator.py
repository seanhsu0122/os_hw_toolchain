import torch
from transformers import pipeline, BitsAndBytesConfig
import os

LLM_PIPELINE = None

def _initialize_llm():
    """載入本地 Llama-8B 模型。"""
    global LLM_PIPELINE
    if LLM_PIPELINE is None:
        print("首次載入 Llama-8B 模型 (4-bit 量化)，請稍候...")
        
        # 設定 4-bit 量化
        quantization_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.bfloat16
        )

        # 確保有足夠的 VRAM，或在 CPU 上運行（會非常慢）
        LLM_PIPELINE = pipeline(
            "text-generation",
            model="meta-llama/Meta-Llama-3-8B-Instruct",
            model_kwargs={
                "torch_dtype": torch.bfloat16,
                "quantization_config": quantization_config
            },
            device_map="auto",
        )
        print("Llama-8B 模型載入完成。")

def _query_llama(prompt_text: str) -> str:
    """使用本地 Llama 模型生成回應。"""
    if LLM_PIPELINE is None:
        _initialize_llm()

    messages = [
        {"role": "user", "content": prompt_text},
    ]
    
    outputs = LLM_PIPELINE(
        messages,
        max_new_tokens=1024, # 增加 token 數量以容納腳本
        do_sample=True,
        temperature=0.7,
        top_p=0.9,
    )
    # 從 pipeline 的輸出中提取助理的回應
    response = outputs[0]["generated_text"]
    if isinstance(response, list):
        return response[-1].get('content', '')
    return ""


def generate_script(question: str, language: str = "English") -> str:
    """
    Generate a conversational script for a video presentation directly from a question.
    The script will be between approximately 30 seconds and 1 minute long.

    :param question: The user's original input question
    :param language: The language for the output script
    :return: The generated conversational script
    """
    prompt = f"""
    Your task is to generate a conversational script for a video presentation based on the following question.
    First, formulate a clear and concise answer to the question.
    Then, based on your answer, create the script.
    The script should be in {language}.
    The script should be between 30 seconds and 1 minute long.
    Use simple, easy-to-understand language and avoid technical jargon.
    Your output MUST be only the script text itself, without any additional explanations, titles, or formatting like "Scenario Description:" or "Script:".

    Question:
    {question}
    """
    return _query_llama(prompt)

def generate_image_prompt(question: str, script_text: str) -> str:
    """
    Generates a descriptive prompt for an image generation model based on a question and its corresponding script.

    :param question: The user's original input question.
    :param script_text: The video script (the answer).
    :return: A descriptive prompt for image generation.
    """
    prompt = f"""
    Your task is to act as a concept artist. Your goal is to create a highly concise and impactful image prompt for an AI image generator (like Stable Diffusion). This image will serve as an explanatory background for a video.

    **Instructions:**
    1.  **Synthesize the Core Concept:** Read the original question and the video script (the answer). Your main goal is to find the central idea that connects the question to the answer.
    2.  **Look Beyond Metaphors:** The script might use analogies or metaphors to explain a concept. Do not illustrate the metaphor literally. Instead, identify the **underlying principle** the metaphor is trying to explain.
    3.  **Create a Visual Concept:** Design a symbolic, minimalist visual that represents this underlying principle. The visual must be relevant to both the question's topic and the script's explanation.
    4.  **Generate the Prompt:** Write a short, keyword-focused prompt in English that describes this visual concept.

    **Constraints:**
    - The prompt must be concise (5-15 words).
    - The prompt must describe an **illustration, infographic, or conceptual art**. Avoid realistic photos.
    - The prompt must NOT contain any text, letters, or numbers.
    - Your final output MUST be ONLY the prompt text itself, with no extra explanations or labels like "Image Prompt:".

    **Original Question:**
    {question}

    **Video Script (Answer):**
    {script_text}
    """
    return _query_llama(prompt)


if __name__ == "__main__":
    # Test script generator
    print("--- Generating Script ---")
    question = "What is a quantum computer?\nAnd how is it different from a classical computer?"
    
    try:
        script = generate_script(question, language="English")
        print(f"Original question: {question}")
        print("-" * 20)
        print("Generated Script:")
        print(script)

        print("\n--- Generating Image Prompt ---")
        image_prompt = generate_image_prompt(question, script)
        print(f"From Question: {question}")
        print(f"From Script: {script[:100]}...")
        print("-" * 20)
        print("Generated Image Prompt:")
        print(image_prompt)

    except Exception as e:
        print(f"An error occurred: {e}")