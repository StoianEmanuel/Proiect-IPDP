FROM python:3.11-slim-bullseye
COPY . /app
WORKDIR /app/API
RUN pip install -r ./requirements.txt
RUN apt-get update && apt-get install -y sqlite3
RUN adduser --disabled-password myuser
USER myuser
ENV HOST=0.0.0.0
ENV PORT=7090
EXPOSE 7090
ENTRYPOINT [ "python" ]
CMD ["hardware.py"]