from fastapi import FastAPI, Depends, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from pydantic import BaseModel, Field
from typing import Optional
from dotenv import load_dotenv

import uvicorn
import json
import os
import requests

load_dotenv()
API_KEY = os.getenv("API_KEY")
if API_KEY is None:
    raise ValueError("API_KEY is missing. Put it in env or .env and load it.")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_FILE_PATH = os.path.join(BASE_DIR, "DB_movies.json")
#URL_OMD = f"https://www.omdbapi.com/?t={movie_title}&apikey={API_KEY}"


app = FastAPI()

# Serve static files (like CSS)
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory=BASE_DIR)

class Movie(BaseModel):
    id: int
    title: str 
    year: int 
    director: str 
    rating: float 
    poster: str 

class Movie_omd(BaseModel):
    id: Optional[int] = None
    title: str = Field(alias="Title")
    year: int = Field(alias="Year")
    director: str = Field(alias="Director")
    rating: float = Field(alias="imdbRating")
    poster: str = Field(alias="Poster", default="N/A")


def _get_active_file_path(file_path: str = DEFAULT_FILE_PATH) -> str:
    return file_path

def read_json_file(file_path: str) -> list:
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    try: 
        with open(file_path, 'r') as file:
            data = json.load(file)
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail="Error reading JSON file") from e
    
    if not isinstance(data, list):
        raise HTTPException(status_code=500, detail="Invalid data format in JSON file")
    return data
    
def write_json_file(movies: list, file_path: str) -> list:
    with open(file_path, 'w') as file:
        json.dump(movies, file, indent=4)
        return movies
    
def find_movie_by_id(movie_id: int, file_path: str) -> dict:
    '''
    Find a movie by its ID.
    Args:   
        movie_id (int): The ID of the movie to find.
        file_path (str): The path to the JSON file.
    Returns:
        dict: The movie with the given ID.  
        Raises HTTPException if the movie is not found.
    '''
    if movie_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid movie ID")

    current_movies = get_movies(file_path)
    for i, movie in enumerate(current_movies):
        if movie["id"] == movie_id:
            return {"index": i, "movie": movie}
    raise HTTPException(status_code=404, detail="Movie not found")


@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI for movies!"}

@app.get("/omd", response_model=Movie_omd)
def get_omd_movie(movie_title: str) -> dict:
    """
    Get a movie from the OMDb API.
    Args:
        movie_title (str): The title of the movie to search for.
    Returns:
        dict: The movie data from the OMDb API.
    """
    url = f"https://www.omdbapi.com/?t={movie_title}&apikey={API_KEY}"
    response = requests.get(url)
    return response.json()


@app.get("/movies", response_model=list[Movie])
def get_movies(file_path: str = Depends(_get_active_file_path)) -> list:
    """
    Get all movies from the JSON file.
    Args:
        file_path (str): The path to the JSON file.
    Returns:
        list: The list of movies.
    """
    return read_json_file(file_path)

@app.post("/movies", response_model=Movie_omd)
def create_movie_omd(movie: Movie_omd, file_path: str = Depends(_get_active_file_path)) -> dict:
    """
    Create a new movie in the JSON file from the OMDb API.
    Args:
        movie_title (str): The title of the movie to create.
        file_path (str): The path to the JSON file.
    Returns:
        dict: The created movie.
    """
    current_movies = read_json_file(file_path)
    if current_movies:
        next_id = current_movies[-1]["id"] + 1
    else:
        next_id = 1

    movie.id = next_id
    current_movies.append(movie.model_dump())
    write_json_file(current_movies, file_path)
    return movie

@app.get("/movies/{movie_id}")
def get_movie_by_movie_id(movie_id : int, file_path: str = Depends(_get_active_file_path)) -> dict:
    """
    Read a movie from the JSON file.
    Args:
        movie_id (int): The ID of the movie to read.
        file_path (str): The path to the JSON file.
    Returns:
        dict: The read movie.
    """
    try:
        result = find_movie_by_id(movie_id, file_path)
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail) from e
    
    try:
        movie = result["movie"]
        return movie
    except HTTPException as e:
        raise HTTPException(status_code=404, detail="Movie not found") from e

@app.put("/movies/{movie_id}", response_model=Movie)
def update_movie(movie_id: int, movie: Movie, file_path: str = Depends(_get_active_file_path)):
    current_movies = read_json_file(file_path)
    for i, existing in enumerate(current_movies):
        if existing["id"] == movie_id:
            current_movies[i] = movie.model_dump()
            write_json_file(current_movies, file_path)
            return movie.model_dump()
    return {"error": "Movie not found"}

@app.delete("/movies/{movie_id}")
def delete_movie(movie_id: int, file_path: str = Depends(_get_active_file_path)):
    current_movies = read_json_file(file_path)
    for i, existing in enumerate(current_movies):
        if existing["id"] == movie_id:
            deleted_movie = current_movies.pop(i)
            write_json_file(current_movies, file_path)
            return deleted_movie
    return {"error": "Movie not found"}


@app.get("/html", response_class=FileResponse)
async def read_html(request: Request, movies: Movie = Depends(get_movies)) -> FileResponse:
    """
    Render the HTML template for the movie page.
    Args:
        request (Request): The request object.
    Returns:
        FileResponse: The HTML template.
    """
    return templates.TemplateResponse("html_movie.html", {"request": request, "movies": movies})



if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)