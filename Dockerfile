FROM python:3.15

WORKDIR /HIVEBOX

COPY src/ /HIVEBOX/

COPY requirements.txt /HIVEBOX/

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 80
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]