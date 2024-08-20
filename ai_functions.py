import requests
import json

RAPIDAPI_KEY = os.getenv('RAPIDAPI_KEY')
URL = "https://chatgpt-42.p.rapidapi.com/conversationgpt4-2"


def chat_with_gpt(prompt, system_prompt=""):
    payload = {
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "system_prompt": system_prompt,
        "temperature": 0.9,
        "top_k": 5,
        "top_p": 0.9,
        "max_tokens": 256,
        "web_access": False
    }
    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": "chatgpt-42.p.rapidapi.com",
        "Content-Type": "application/json"
    }

    response = requests.post(URL, json=payload, headers=headers)
    return response.json()['result']


def get_movie_recommendations(favorite_movies):
    prompt = (f"Based on these favorite movies: {', '.join(favorite_movies)}, can you recommend 5 other movies? Just "
              f"list the titles.")
    return chat_with_gpt(prompt)


def generate_movie_review(movie_title):
    prompt = (f"Write a brief review for the movie '{movie_title}'. Include your opinion on the plot, acting, "
              f"and overall experience.")
    return chat_with_gpt(prompt)


def generate_movie_trivia(movie_title):
    prompt = f"Give me 3 interesting trivia facts about the movie '{movie_title}'."
    return chat_with_gpt(prompt)
