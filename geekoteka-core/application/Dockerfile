FROM python:3.9

ENV FLASK_APP=app.py
ENV FLASK_ENV=development

RUN pip install flask bcrypt



COPY . /app

WORKDIR /app

EXPOSE 5000

CMD ["flask", "run", "--host=0.0.0.0"]
