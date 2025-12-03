FROM python:3.12-alpine

WORKDIR /myapp

COPY Pipfile* ./

RUN pip install --no-cache-dir pipenv && \
    pipenv install --system --deploy --clear && \
    pip uninstall pipenv -y

COPY app.py .
COPY views ./views/
CMD ["python3", "app.py"]
