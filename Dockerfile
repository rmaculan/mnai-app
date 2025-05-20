# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Collect static files (if applicable for your Django setup)
# RUN python manage.py collectstatic --noinput

# Apply database migrations (if applicable)
# RUN python manage.py migrate

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Run the application using Daphne (suitable for Channels)
# Replace 'backend.asgi:application' with the correct path to your ASGI application if different
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "backend.asgi:application"]

# If you were using Gunicorn for a standard WSGI app:
# CMD ["gunicorn", "--bind", "0.0.0.0:8000", "backend.wsgi:application"]

# If you were using Django's development server (not recommended for production):
# CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
