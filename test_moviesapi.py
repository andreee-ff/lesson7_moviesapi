import pytest
import os
import json
from pathlib import Path
from .main import app, _get_active_file_path
from .main import read_json_file, write_json_file
from fastapi.testclient import TestClient

TEST_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEST_FILE_PATH = "DB_test_movies.json"
TEST_MOVIES = [
    {
        "id": 1,
        "title": "Avatar",
        "year": 2009,
        "director": "James Cameron",
        "rating": 7.9,
        "poster": "https://"
    },
    {
        "id": 2,
        "title": "The Dark Knight",
        "year": 2008,
        "director": "Christopher Nolan",
        "rating": 9.0,
        "poster": "https://"
    }

    ]  # Sample data

# Override the dependency to use the test file path
app.dependency_overrides[_get_active_file_path] = lambda: TEST_FILE_PATH

client = TestClient(app)
#app = FastAPI()

@pytest.fixture
def tmp_movies_file(tmp_path: Path, test_movies: list = TEST_MOVIES) -> Path:
    """
    Create a temporary JSON file for testing.
    Args:
        tmp_path: pytest fixture that provides a temporary directory.
        test_movies (list): List of movies to write to the test file.
    """
    tmp_file_path = tmp_path / TEST_FILE_PATH
    with open(tmp_file_path, 'w') as f:
        json.dump(test_movies, f, indent=4)
    return str(tmp_file_path)

@pytest.fixture()
def override_get_active_file_path(tmp_movies_file: Path):
    """
    Override the _get_active_file_path dependency to use the temporary test file.
    Args:
        tmp_movies_file (Path): The path to the temporary test file.
    """
    app.dependency_overrides[_get_active_file_path] = lambda: str(tmp_movies_file)
    yield
    app.dependency_overrides.clear()

def test_write_json_file(tmp_movies_file: Path):
    written_movies = write_json_file(TEST_MOVIES, str(tmp_movies_file))
    assert written_movies == TEST_MOVIES
    with open(tmp_movies_file, 'r') as f:
        data = json.load(f)
    assert data == TEST_MOVIES

def test_read_json_file(tmp_movies_file: Path):
    data = read_json_file(tmp_movies_file)
    assert data == TEST_MOVIES


def test_get_movies_file_not_found():
    app.dependency_overrides[_get_active_file_path] = lambda: "non_existent_file.json"
    response = client.get("/movies")
    assert response.status_code == 404
    assert response.json() == {"detail": "File not found"}

def test_get_movies_invalid_json(tmp_path: Path):
    invalid_file_path = tmp_path / "invalid_movies.json"
    with open(invalid_file_path, 'w') as f:
        f.write("Invalid JSON content")
    app.dependency_overrides[_get_active_file_path] = lambda: str(invalid_file_path)
    response = client.get("/movies")
    assert response.status_code == 500
    assert response.json() == {"detail": "Error reading JSON file"}

def test_get_movies(override_get_active_file_path):
    response = client.get("/movies")
    print("RETURNING:", response.json())
    assert response.status_code == 200
    assert response.json() == TEST_MOVIES

'''
@pytest.mark.parametrize("movie_id, expected_status, expected_response", 
[
    (1, 200, TEST_MOVIES[0]), # Existing movie
    (99, 404, {"detail": "Movie not found"}),  # Non-existing movie
    (-1, 400, {"detail": "Invalid movie ID"}), # Invalid ID
    ("abc", 422, None)  # Invalid type
])

def test_get_movie_by_id_parametrized(movie_id, expected_status, expected_response):
    response = client.get(f"/movies/{movie_id}")
    assert response.status_code == expected_status
    if expected_response:
        assert response.json() == expected_response
'''
def test_get_movie_by_id(override_get_active_file_path):
    movie_id = 1
    response = client.get(f"/movies/{movie_id}")
    assert response.status_code == 200
    assert response.json() == TEST_MOVIES[movie_id - 1]

def test_get_movie_by_id_not_found(override_get_active_file_path):
    movie_id = 99
    response = client.get(f"/movies/{movie_id}")
    assert response.status_code == 404
    assert response.json() == {"detail": "Movie not found"}

def test_get_movie_by_id_invalid(override_get_active_file_path):
    movie_id = -1
    response = client.get(f"/movies/{movie_id}")
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid movie ID"}

def test_get_movie_by_id_incalid_text(override_get_active_file_path):
    movie_id = "sdfg"
    response = client.get(f"/movies/{movie_id}")
    assert response.status_code == 422


