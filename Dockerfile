FROM python:3.11-slim

WORKDIR /app

COPY . .
RUN pip3 install -e .
RUN python setup.py build

CMD ["/bin/bash", "-c", "python -m chiyakbot.bot production"]

