def image_checker(GAME_LANGUAGE, IMAGE_URL):
    from pathlib import Path
    import hashlib
    import google.generativeai as genai
    from dotenv import load_dotenv
    import os
    import json
    import random
    from googletrans import Translator

    load_dotenv()
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

    # GAME_THEME = GAME_THEME

    genai.configure(api_key=GEMINI_API_KEY)

    # Set up the model
    generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 0,
    "max_output_tokens": 8192,
    "response_mime_type": "application/json",
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

    model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest",
                                generation_config=generation_config,
                                safety_settings=safety_settings)
    
    uploaded_files = []
    def upload_if_needed(pathname: str) -> list[str]:
        path = Path(pathname)
        hash_id = hashlib.sha256(path.read_bytes()).hexdigest()
        try:
            existing_file = genai.get_file(name=hash_id)
            return [existing_file]
        except:
            pass
        uploaded_files.append(genai.upload_file(path=path, display_name=hash_id))
        return [uploaded_files[-1]]
    
    path_of_image = 'assets/' + IMAGE_URL

    prompt_parts = [
        "input:Tell me all the objects you see in this image and their confidence values and pixel coordinates ",
        *upload_if_needed(path_of_image),
        "output: ",
        ]

    image_checker_response = model.generate_content(prompt_parts)
    image_checker_json_response = json.loads(image_checker_response.parts[0].text)

    picked_object = random.choice(image_checker_json_response)

    picked_object_word = picked_object['object']
    picked_object_x_coordinate = (picked_object['x_max'] + picked_object['x_min']) / 2
    picked_object_y_coordinate = (picked_object['y_max'] + picked_object['y_min']) / 2

    # # Set up the model
    # image_checker_generation_config = {
    #     "temperature": 1,
    #     "top_p": 0.95,
    #     "top_k": 0,
    #     "max_output_tokens": 8192,
    #     "response_mime_type": "application/json",
    # }

    # image_checker_model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest",
    #                                             generation_config=image_checker_generation_config,
    #                                             safety_settings=safety_settings)
    
    # checker_prompt_parts = [
    #     "input: Tell me whether or not the word {picked_object_word} belongs to the category of {GAME_THEME}. Limit your output to 'True' or 'False'.",
    #     "output: ",
    #     ]
    
    # checker_response = image_checker_model.generate_content(checker_prompt_parts)
    # checker_response_json_response = json.loads(checker_response.parts[0].text)

    # if checker_response_json_response[0] == 'True':
    #     pass
    # else:
    #     return False
    
    related_word_generator_prompt_parts = [
        "input: Give me 5 words closely related to the word: {picked_object_word}.",
        "output: ",
        ]

    related_word_generator_response = model.generate_content(related_word_generator_prompt_parts)
    related_word_generator_json_response = json.loads(related_word_generator_response.parts[0].text)

    translator = Translator()

    translated_picked_object_word = translator.translate(picked_object_word, dest=GAME_LANGUAGE).text
    translated_related_words = [translator.translate(word, dest=GAME_LANGUAGE).text for word in related_word_generator_json_response]

    translated_related_word1 = translated_related_words[0]
    translated_related_word2 = translated_related_words[1]
    translated_related_word3 = translated_related_words[2]
    translated_related_word4 = translated_related_words[3]
    translated_related_word5 = translated_related_words[4]

    return translated_picked_object_word, picked_object_x_coordinate, picked_object_y_coordinate, translated_related_word1, translated_related_word2, translated_related_word3, translated_related_word4, translated_related_word5