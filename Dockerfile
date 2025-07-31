FROM python:3.11-slim

WORKDIR /code

COPY requirements.txt /code/
RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY . /code

CMD ["fastapi", "run", "app/main.py", "--host", "0.0.0.0", "--port", "8000"]