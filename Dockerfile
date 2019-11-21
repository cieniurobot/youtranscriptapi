FROM python:3.6

ENV PYTHONUNBUFFERED 1
RUN mkdir -p /opt/youtranscript_api
WORKDIR /opt/youtranscript_api
COPY . /opt/youtranscript_api/
RUN pip install --upgrade pip
RUN pip install pipenv && pipenv install --system

EXPOSE 8001
CMD ["gunicorn", "-c", "config/gunicorn/conf.py", "--bind", ":8001", "--chdir", "src", "wsgi:application"]
