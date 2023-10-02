FROM python:2.7.18-slim-buster

# Set the working directory
WORKDIR /app

# Expose the port the app will run on
EXPOSE 8000

# Copy the requirements file into the container
COPY requirements.txt /app/

# Install dependencies and upgrade pip
RUN apt-get update && \
    apt-get install -y libmariadb-dev-compat gcc build-essential default-libmysqlclient-dev && \
    python -m pip install --upgrade pip && \
    pip2 install -r requirements.txt --no-cache-dir && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy the rest of the application code
COPY . /app

# Set the command to run the application
ENTRYPOINT ["python"]
CMD ["manage.py", "runserver", "0.0.0.0:8000"]
