from fastapi import FastAPI
import uvicorn

app = FastAPI()
movies = [
    {"id": 1, "title": "Alice", "year": 2021, "director": "Director A", "rating": 8.5},
    {"id": 2, "title": "Bob", "year": 2020, "director": "Director B", "rating": 7.9},
    {"id": 3, "title": "Charlie", "year": 2019, "director": "Director C", "rating": 9.1}
    ]  # Sample data


@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI for movies!"}


@app.get("/movies")
def get_users():
    return movies


@app.post("/movies")
def create_user(movie: dict):
    movies.append(movie)
    return movie

@app.get("/movies/{movie_id}")
def read_movie(movie_id : int):
    for movie in movies:
        if movie["id"] == movie_id:
            return movie
    return {"error": "Movie not found"}



"""
@app.put("/movies/{movie_id}")
def update_user(movie_id: int, movie: dict):
    for i, u in enumerate(movies):
        if u["id"] == movie_id:
            movies[i] = movie
            return movie
    return {"error": "Movie not found"}
"""
"""
@app.post("/movies")
def create_user(user: dict):
    users.append(user)
    return user


@app.put("/users/{user_id}")
def update_user(user_id: int, user: dict):
    for i, u in enumerate(users):
        if u["id"] == user_id:
            users[i] = user
            return user
    return {"error": "User not found"}


@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    for i, u in enumerate(users):
        if u["id"] == user_id:
            return users.pop(i)
    return {"error": "User not found"}
"""

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
