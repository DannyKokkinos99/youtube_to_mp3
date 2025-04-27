# Use an official Python runtime as a parent image
FROM python:3.12-alpine

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY static /app/static
COPY templates /app/templates
COPY utility /app/utility
COPY app.py /app/app.py
COPY functions.py /app/functions.py
COPY requirements.txt /app/requirements.txt

# Install any necessary packages specified in requirements.txt
RUN apk add --no-cache ffmpeg
RUN pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 5005

# Command to run the application
CMD ["python", "app.py"]