from fastapi import FastAPI
import uvicorn
import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_PATH = os.path.join(BASE_DIR, "list_movies.json")

app = FastAPI()
"""
movies = [
    {"id": 1, "title": "Alice", "year": 2021, "director": "Director A", "rating": 8.5},
    {"id": 2, "title": "Bob", "year": 2020, "director": "Director B", "rating": 7.9},
    {"id": 3, "title": "Charlie", "year": 2019, "director": "Director C", "rating": 9.1}
    ]  # Sample data
"""

def read_json_file() -> list:
    with open(FILE_PATH, 'r') as file:
        return json.load(file)
    
def write_json_file(movies) -> None:
    with open(FILE_PATH, 'w') as file:
        json.dump(movies, file, indent=4)

movies = read_json_file()


@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI for movies!"}


@app.get("/movies")
def get_users() -> list:
    return movies


@app.post("/movies")
def create_user(movie: dict) -> dict:
    movies.append(movie)
    write_json_file(movies)
    return movie

@app.get("/movies/{movie_id}")
def read_movie(movie_id : int):
    for movie in movies:
        if movie["id"] == movie_id:
            return movie
    return {"error": "Movie not found"}

@app.post("/movies")
def create_movie(movie: dict) -> dict:
    movies.append(movie)
    write_json_file(movies)
    return movie

@app.put("/movies/{movie_id}")
def update_movie(movie_id: int, movie: dict):
    for i, u in enumerate(movies):
        if u["id"] == movie_id:
            movies[i] = movie
            write_json_file(movies)
            return movie
    return {"error": "Movie not found"}


@app.delete("movies/{movies_id}")
def delete_movie(movie_id: int):
    for i, u in enumerate(movies):
        if u["id"] == movie_id:
            deleted_movie = movies.pop(i)
            write_json_file(movies)
            return deleted_movie
    return {"error": "Movie not found"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
