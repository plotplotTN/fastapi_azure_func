FROM python:3.9-slim


ENV DOCKER_REGISTRY containerregistryfortraducterapi

# Upgrade pip and install requirements
COPY requirements.txt requirements.txt
RUN pip install -U pip
RUN pip install -r requirements.txt

# Copy the rest of the files
WORKDIR /app
COPY . .

EXPOSE 8000

# Run the app
ENTRYPOINT python -m uvicorn main:app --reload --port 8000 --host 0.0.0.0