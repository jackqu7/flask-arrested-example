FROM python:3.5

RUN mkdir /opt/code
ADD . /opt/code
WORKDIR /opt/code

RUN pip install -U pip
RUN pip install -r requirements.txt
RUN python setup.py develop

ENV PORT 5000
ENV HOST 0.0.0.0
ENV FLASK_APP=app.py

VOLUME ["/opt/code"]

CMD ["flask", "run", "--host=0.0.0.0"]
