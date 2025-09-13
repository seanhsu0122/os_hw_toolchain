import google.generativeai as genai

from config import GEMINI_API_KEY

# 設定 Gemini API 金鑰
genai.configure(api_key=GEMINI_API_KEY)

def generate_answer(question: str) -> str:
    """
    使用 Google Gemini API 生成問題的回答。

    :param question: 使用者輸入的問題
    :return: Gemini 模型生成的回答
    """
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(question)
    return response.text.strip()

def answer_to_script(answer: str) -> str:
    """
    將詳細的回答內容，轉換成適合影片講解的口語化演講稿。
    演講稿的長度會被控制在約 30 秒至 1 分鐘之間。

    :param answer: LLM 生成的原始回答
    :return: 轉換後的口語化演講稿
    """
    model = genai.GenerativeModel('gemini-1.5-flash')

    # 設計提示詞，將 LLM 的回答轉換成口語化且適合講解的演講稿
    prompt = f"""
    請將以下這段關於「量子電腦」的回答，轉換成一段長度約30秒到1分鐘、口語化且適合用於影片講解的演講稿。
    請使用簡單易懂的詞彙，避免過多專業術語，讓非技術背景的觀眾也能理解。
    
    原始回答：
    {answer}
    """
    
    response = model.generate_content(prompt)
    return response.text.strip()

if __name__ == "__main__":
    # 測試腳本生成器
    print("--- 步驟 1: 產生回答 ---")
    question = "什麼是量子電腦？"
    
    try:
        raw_answer = generate_answer(question)
        print(f"原始問題：{question}")
        print("-" * 20)
        print("LLM 原始回答：")
        print(raw_answer)

        print("\n--- 步驟 2: 轉換為演講稿 ---")
        script = answer_to_script(raw_answer)
        print("-" * 20)
        print("轉換後演講稿：")
        print(script)

    except Exception as e:
        print(f"發生錯誤：{e}")
        print("請檢查您的 GEMINI_API_KEY 是否正確設定。")
