# Dockerfile
# Use an official Python runtime as a parent image
FROM python:3.10.19-slim

# Copy uv binary from the official uv image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY pyproject.toml uv.lock ./

# Install any needed packages specified in requirements.txt
RUN uv sync --frozen --no-dev

# Copy the Flask application code into the container
COPY . .

# Expose the port your Flask app listens on
EXPOSE 5000

# Define the command to run your Flask application
CMD ["uv", "run", "python", "main.py"]