FROM python:3.10

RUN apt-get update && apt-get install -y ffmpeg tesseract-ocr libtesseract-dev

COPY . .

RUN pip install -r requirements.txt

CMD ["streamlit", "run", "app.py"]
