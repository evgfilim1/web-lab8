FROM python:3.10-slim
EXPOSE 80
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -Ur requirements.txt
COPY . ./
ENV FLASK_APP="main:app"
ENTRYPOINT ["/usr/local/bin/python", "-m", "flask", "run", "-h", "0.0.0.0", "-p", "80"]
