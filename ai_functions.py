import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

GROQ_API_KEY = os.getenv('GROQ_API_KEY')
client = Groq(api_key=GROQ_API_KEY)


def chat_with_groq(prompt, system_prompt=""):
    completion = client.chat.completions.create(
        model="llama-3.1-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        temperature=0.9,
        max_tokens=256,
        top_p=0.9,
        stream=False
    )
    return completion.choices[0].message.content


def get_movie_recommendations(favorite_movies):
    prompt = f"Based on these favorite movies: {', '.join(favorite_movies)}, can you recommend 5 other movies? Just list the titles, one per line."
    response = chat_with_groq(prompt)
    recommendations = [movie.strip() for movie in response.split('\n') if movie.strip()]
    return recommendations


def generate_movie_review(movie_title):
    prompt = f"Write a brief, engaging review for the movie '{movie_title}'. Include your opinion on the plot, acting, and overall experience. Keep it under 150 words."
    return chat_with_groq(prompt)


def generate_movie_trivia(movie_title):
    prompt = f"Give me 3 interesting trivia facts about the movie '{movie_title}'. Format each fact as a complete sentence."
    response = chat_with_groq(prompt)
    facts = [fact.strip() for fact in response.split('\n') if fact.strip()]
    return facts
