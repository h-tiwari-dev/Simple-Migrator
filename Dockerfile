# Use an official Python runtime as a parent image
FROM python:3.10

# Set the working directory to /app
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

COPY . /app
COPY pyproject.toml /app 
WORKDIR /app
ENV PYTHONPATH=${PYTHONPATH}:${PWD} 
RUN pip3 install poetry
RUN poetry config virtualenvs.create false
RUN poetry install --no-dev


# Set environment variables for connecting to MySQL
ENV DATABASE_URL=mysql://root:alpha123@mysql:3306/testdb

RUN cd test
# Command to run on container start
CMD ["poetry", "run", "python", "-m", "unittest"]

