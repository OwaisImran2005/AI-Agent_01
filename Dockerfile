FROM python:3.11

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Hugging Face expects apps to run on port 7860
CMD ["chainlit", "run", "main.py", "--port", "7860"]