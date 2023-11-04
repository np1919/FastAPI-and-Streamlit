# Use the official Python image as a parent image
FROM tiangolo/uvicorn-gunicorn-fastapi

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt /app/

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

# Copy the rest of your application's source code to the container
COPY . /app/

# Expose port 80 to the outside world
EXPOSE 80

# Define the command to run your FastAPI application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]