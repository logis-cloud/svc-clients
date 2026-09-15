FROM python:3.11-slim

WORKDIR /code

# pymysql es un driver 100% Python: no requiere gcc ni libmysqlclient-dev,
# por eso no se instala nada por apt-get (evita depender de mirrors de Debian).
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app ./app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
