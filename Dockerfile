FROM python:3.10-slim
COPY . /app
WORKDIR /app/API
RUN pip install -r ./requirements.txt
RUN adduser --disabled-password myuser
USER myuser
ENTRYPOINT [ "python" ]
CMD ["hardware.py"]