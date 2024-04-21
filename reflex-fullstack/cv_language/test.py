import os
from gemini_image_checker import image_checker


GAME_LANGUAGE = "Korean"
IMAGE_URL = "mouse_keyboard.jpg"


translated_picked_object_word, picked_object_x_coordinate, picked_object_y_coordinate, translated_related_word1, translated_related_word2, translated_related_word3, translated_related_word4, translated_related_word5 = image_checker(GAME_LANGUAGE, IMAGE_URL)
print(translated_picked_object_word,
        picked_object_x_coordinate,
        picked_object_y_coordinate,
        translated_related_word1,
        translated_related_word2,
        translated_related_word3,
        translated_related_word4,
        translated_related_word5)