import requests

BASE_URL = "http://localhost:8000"
def test_get_question_success(setup_database):
    """
    Tests successfully fetching a random question via HTTP.
    The `setup_database` fixture ensures the DB is ready.
    """
    response = requests.get(f"{BASE_URL}/api/question/?round=Jeopardy!&value=$200")
    assert response.status_code == 200
    data = response.json()
    assert data["round"] == "Jeopardy!"
    assert data["value"] == "$200"
    assert "question_id" in data
    assert "category" in data
    assert "question" in data

def test_get_question_invalid_value_format():
    """
    Tests the endpoint's response to a badly formatted value.
    This test does not require database setup.
    """
    response = requests.get(f"{BASE_URL}/api/question/?round=Jeopardy!&value=200")
    assert response.status_code == 400
    assert "Invalid value format" in response.json()["detail"]

def test_get_question_not_found(setup_database):
    """
    Tests requesting a question that doesn't exist in the test data.
    """
    response = requests.get(f"{BASE_URL}/api/question/?round=Jeopardy!&value=$9999")
    assert response.status_code == 404
    assert "No questions found" in response.json()["detail"]

def test_verify_answer_correct(setup_database):
    """
    Tests verifying a correct answer via an HTTP POST request.
    """
    response = requests.post(
        f"{BASE_URL}/api/verify-answer/",
        json={"question_id": 1, "user_answer": "Copernicus"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["is_correct"] is True
    assert "ai_response" in data

def test_verify_answer_incorrect(setup_database):
    """
    Tests verifying an incorrect answer via an HTTP POST request.
    """
    response = requests.post(
        f"{BASE_URL}/api/verify-answer/",
        json={"question_id": 1, "user_answer": "Ptolemy"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["is_correct"] is False

def test_verify_answer_with_typo(setup_database):
    """
    Tests that the API (in offline mode) marks a typo as incorrect.
    The fallback is a simple string comparison and will not pass typos.
    """
    response = requests.post(
        f"{BASE_URL}/api/verify-answer/",
        json={"question_id": 1, "user_answer": "Copernics"},  # Intentional typo
    )
    assert response.status_code == 200
    data = response.json()
    assert data["is_correct"] is False

def test_verify_answer_question_not_found(setup_database):
    """
    Tests verifying an answer for a question ID that does not exist.
    """
    response = requests.post(
        f"{BASE_URL}/api/verify-answer/",
        json={"question_id": 9999, "user_answer": "Doesn't matter"},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Question not found"
