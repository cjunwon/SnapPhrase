def generate_theme_and_count():
        from pathlib import Path
        import hashlib
        import google.generativeai as genai
        import random
        from dotenv import load_dotenv
        import os

        load_dotenv()
        GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

        genai.configure(api_key=GEMINI_API_KEY)

        # Set up the model
        generation_config = {
            "temperature": 1,
            "top_p": 0.95,
            "top_k": 0,
            "max_output_tokens": 8192,
        }

        safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
        ]

        theme_count_model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest",
                                                                    generation_config=generation_config,
                                                                    safety_settings=safety_settings)

        theme_list = ['education',
                                    'technology',
                                    'furniture']

        theme_combined = ", ".join(theme_list)

        theme_prompt_parts = [
            "input: Pick one theme from the following list of themes: {}".format(theme_combined),
            "output: ",
        ]

        theme_response = theme_count_model.generate_content(theme_prompt_parts)

        theme_picked = theme_response.parts[0].text

        # random number generator
        count_picked = random.randint(1, 5)

        return theme_picked