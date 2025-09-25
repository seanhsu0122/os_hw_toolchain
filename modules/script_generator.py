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
        repetition_penalty=1.15, # 加入重複懲罰以減少重複文字
        return_full_text=False,  # 僅回傳 AI 生成的部分
    )
    # 從 pipeline 的輸出中提取助理的回應
    response = outputs[0]["generated_text"]

    # 嘗試釋放 VRAM 給下一個模型使用
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        
    # 因為 return_full_text=False，回應直接就是我們需要的內容
    return response.strip()


def generate_script(question: str, language: str = "English") -> str:
    """
    Generate a conversational script for a video presentation directly from a question.
    The script will be approximately one minute long.

    :param question: The user's original input question
    :param language: The language for the output script
    :return: The generated conversational script
    """
    prompt = f"""
    Your task is to act as a student answering a teacher's question. Generate a script for this answer.
    The script should be a clear, concise, and direct answer to the question provided.
    The tone should be respectful and knowledgeable, like a good student explaining a concept.
    The script should be in {language}.
    The total speaking time for the script should be approximately one minute.

    **CRITICAL INSTRUCTIONS:**
    1.  **START DIRECTLY:** Begin the script immediately with the answer. Do NOT repeat the question or use introductory phrases like "The answer to the question is...".
    2.  **CONCISE AND FOCUSED:** Stick to the core of the answer. Avoid unnecessary details or tangents.
    3.  **NO CLOSING REMARKS:** End the script when the answer is complete. Do NOT add summaries, concluding phrases like "And that's how it works," or ask questions like "Does that make sense?".
    4.  **PLAIN TEXT ONLY:** Your output MUST be only the script text itself. Do not include any titles, labels like "Script:", or other formatting.
    5.  **LANGUAGE ADHERENCE:** The entire script must be written strictly in {language}. Do not use pinyin or any other form of romanization. Only use English for universally recognized technical terms or proper nouns (e.g., "CPU", "GPU", "SATA").

    Question from the teacher:
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
    You are an AI assistant that strictly follows instructions. Your task is to generate a concise image prompt.
    Analyze the provided question and script to identify key concepts. Create an image prompt that includes concrete, real-world objects representing these concepts. The image should be visually interesting and relevant to the topic.
    
    **CRITICAL INSTRUCTIONS:**
    1.  **INCLUDE CONCRETE OBJECTS:** The prompt MUST describe one or more tangible, real-world objects. Avoid purely abstract concepts.
    2.  **OUTPUT TEXT ONLY:** Your entire response must be ONLY the prompt text itself.
    3.  **NO PREFIXES:** Do NOT start with "Here is the prompt:", "Image Prompt:", or similar phrases.
    4.  **NO EXTRA TEXT:** Do NOT include any explanations, notes, or apologies.
    5.  **NO QUOTES:** Do NOT wrap the prompt in quotation marks.
    6.  **BE CONCISE:** The prompt must be 5-15 words.

    **EXAMPLE OF PERFECT OUTPUT for "What is a quantum computer?":**
    A futuristic computer with glowing qubits and intricate wiring

    **Now, generate the prompt for the following:**

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