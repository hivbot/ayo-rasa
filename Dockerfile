FROM rasa/rasa:latest-full

USER root

RUN pip install --upgrade pip && \
pip install --no-cache-dir nltk && \
python -m nltk.downloader vader_lexicon -d '/nltk_data' && \
pip install --upgrade spacy && \
python -m spacy download en_core_web_md

COPY ./components /app/components

USER 1001

ENV PYTHONPATH "${PYTHONPATH}:/app"
