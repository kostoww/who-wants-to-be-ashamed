# Who wants to be ashamed?

# Requirements
- [Docker](https://www.docker.com/)
- [Python 3.11+](https://www.python.org/downloads/)
- [OpenAI API Key](https://platform.openai.com/signup) (for interaction)

# Running application

Before anything, you should copy the `.env.example` file to `.env` and fill in the required variables and adjust secrets

```bash
cp .env.example .env
```

## Using Docker compose

If you want to run the application fast, spin up with the docker compose
```bash
docker compose up
```
Note: The data_import service will run first, populating the PostgreSQL database with the question file. 
Once it completes, the web service will start the FastAPI application and the data_import service will be offline, which is expected behavior.

## Using python
If you prefer to run the application without Docker, it is not natively supported right now, but you should have running postgres and match the correct environment variables
Later, just run the main application file: (untested)
```
python app/main.py
```


## How to Play
- Once the Docker containers are running, open your web browser and navigate to http://localhost:8000.
- Click the "Start New Game" button to load a fresh game board.
- Click on any dollar value in a category to open the clue modal.
- Type your answer in the input box and click "Answer". Remember to phrase it in the form of a question!
- The app will tell you if your answer was correct and show the official answer. If you have an OpenAI key configured, you'll get a more detailed explanation.
- Click "Return to Board" to continue playing.

## Running the tests
For now, the project contains only e2e test suite, which might not work, but in future it will handle a major part of the testing
```bash
pytest
```

## API Documentation

Swagger UI is available at [http://localhost:8000/docs](http://localhost:8000/docs) when the application is running.

# Project Structure

```
.
├── app/                  # Core FastAPI application source code
├── data/                 # Data and data import scripts
├── static/               # Frontend assets
├── infra/                # CI/CD related files
├── tests/                # Automated tests
├── .env.example          # Example environment file which should be copied to .env
├── docker-compose.yml    # Starting point for the Docker Compose setup
```

# TODO 
- find the bug for the parsing csv, as there seems to be some inconsistency in the csv file
- fix the broken test execution, as i have no time to fix it now
- extracts logic from the routes in separate service and keep tiny routes
- add better error handling
- add description for the API parameters and handlers