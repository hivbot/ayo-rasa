FROM rasa/rasa:latest-full

WORKDIR /app

COPY ./components /app/components

ENV PYTHONPATH "${PYTHONPATH}:/app"
