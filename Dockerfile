FROM hrishi2861/terabox:heroku
WORKDIR /app
COPY requirements.txt .
RUN uv venv
RUN uv pip install --no-cache-dir -r requirements.txt
RUN apt-get update && apt-get install -y netcat-traditional && rm -rf /var/lib/apt/lists/*
COPY . .
CMD ["bash", "start.sh"]
