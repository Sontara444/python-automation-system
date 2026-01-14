# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . .

# Run the script
# Note: Interactive OAuth requires a browser, which won't work in a headless Docker.
# You need to generate 'token.json' locally first and mount it into the container.
CMD ["python", "src/main.py"]
