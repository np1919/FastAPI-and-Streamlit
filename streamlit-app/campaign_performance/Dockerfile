# Use the official Python image as a parent image
FROM python:3.10

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt /app/

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

# Copy the rest of your application's source code to the container
COPY . /app/

# Expose the port that Streamlit will run on (default is 8501)
EXPOSE 8501

# Define the command to run your Streamlit application
CMD [ "streamlit", "run", "campaign_performance.py", "--server.port=8501", "--server.address=0.0.0.0"]