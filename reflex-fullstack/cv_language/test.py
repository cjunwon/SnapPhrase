import os
from gemini_theme_count import generate_theme_and_count

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

theme, count = generate_theme_and_count(GEMINI_API_KEY)

print(theme)
print(count)