# Use a lightweight Python image
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all your project files into the container
COPY . .

# Hugging Face Spaces uses port 7860
EXPOSE 7860

# Run the Flask app on the correct port
CMD ["flask", "run", "--host=0.0.0.0", "--port=7860"]