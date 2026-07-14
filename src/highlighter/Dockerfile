FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py index.html ./

ARG HIGHLIGHTER_PORT
ENV HIGHLIGHTER_PORT=${HIGHLIGHTER_PORT}
EXPOSE ${HIGHLIGHTER_PORT}

CMD python app.py
