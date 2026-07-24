FROM python:3.9-slim-buster

WORKDIR /myportfolio

# Copy first so that requirements are cached
COPY requirements.txt .

RUN pip3 install -r requirements.txt

COPY . .

CMD ["python3", "-m", "flask", "run", "--host=0.0.0.0"]

EXPOSE 5000