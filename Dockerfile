FROM python:3.7-alpine

WORKDIR /myapp

COPY Pipfile* ./

RUN pip install --no-cache-dir pipenv && \
    pipenv install --system --deploy --clear && \
    pip uninstall pipenv -y

COPY app.py .
CMD ["python3", "app.py"]