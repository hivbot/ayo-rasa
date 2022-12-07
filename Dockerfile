FROM rasa/rasa:latest-full

USER root

COPY ./components /app/components

USER 1001

ENV PYTHONPATH "${PYTHONPATH}:/app"
