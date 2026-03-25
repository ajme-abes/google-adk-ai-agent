FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml .
RUN pip install google-adk google-genai python-dotenv --quiet

COPY . .

EXPOSE 8000

CMD python server.py
