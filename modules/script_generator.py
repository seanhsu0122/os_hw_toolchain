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

def generate_image_prompt(script_text: str) -> str:
    """
    Generates a descriptive prompt for an image generation model based on a video script.

    :param script_text: The video script.
    :return: A descriptive prompt for image generation.
    """
    # The client gets the API key from the environment variable `GEMINI_API_KEY`.
    client = genai.Client()

    prompt = f"""
    Based on the following video script, create a short, descriptive prompt in English for an AI image generator (like Stable Diffusion) to create a suitable background image for the video.
    The prompt should describe a scene, concept, or an abstract visual that captures the essence of the script.
    Focus on visual elements. Do not include text in the prompt.
    Your output MUST be only the prompt text itself, without any additional explanations or titles like "Image Prompt:".

    Video Script:
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
            image_prompt = generate_image_prompt(script)
            print(f"From Script: {script[:100]}...")
            print("-" * 20)
            print("Generated Image Prompt:")
            print(image_prompt)

        except Exception as e:
            print(f"An error occurred: {e}")