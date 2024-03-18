# Use the Python 3.9 slim base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /client

# Copy the current directory contents into the container at /app
COPY . /client

# Install any needed dependencies specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Run app.py when the container launches
CMD ["python", "client.py"]