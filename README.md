# Who wants to be ashamed?

# Requirements
- [Docker](https://www.docker.com/)
- [Python 3.11+](https://www.python.org/downloads/)
- [OpenAI API Key](https://platform.openai.com/signup) (for interaction)

# Running application
## Using Docker compose

If you want to run the application fast, spin up with the docker compose
```bash
docker compose up
```

## Using python
```
run
```


## Running tests
For now the project contains only e2e test suite, which might not work, but in future it will handle major part of the testing
```bash
pytest
```

# TODO 
- find the bug for the parsing csv, as there seems to be some inconsistency in the csv file
- fix the broken test execution, as i have no time to fix it now
- extracts logic from the routes in separate service and keep tiny routes