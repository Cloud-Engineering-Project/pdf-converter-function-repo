FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["functions-framework", "--target=pdf_converter", "--signature-type=event", "--host=0.0.0.0", "--port=8080"]