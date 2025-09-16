from google import genai
import os

def generate_script(question: str, language: str = "English") -> str:
    """
    Generate a conversational script for a video presentation directly from a question.
    The script will be between approximately 30 seconds and 1 minute long.

    :param question: The user's original input question
    :param language: The language for the output script
    :return: The generated conversational script
    """
    # The client gets the API key from the environment variable `GEMINI_API_KEY`.
    client = genai.Client()

    # Prompt to generate a script directly from a question.
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
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    return response.text.strip()

def generate_image_prompt(question: str, script_text: str) -> str:
    """
    Generates a descriptive prompt for an image generation model based on a question and its corresponding script.

    :param question: The user's original input question.
    :param script_text: The video script (the answer).
    :return: A descriptive prompt for image generation.
    """
    # The client gets the API key from the environment variable `GEMINI_API_KEY`.
    client = genai.Client()

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
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    return response.text.strip()


if __name__ == "__main__":
    # Ensure your GEMINI_API_KEY is set as an environment variable before running.
    if "GEMINI_API_KEY" not in os.environ:
        print("Please set the GEMINI_API_KEY environment variable.")
    else:
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