FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy requirements.txt into the container
COPY requirements.txt .

# Install the required packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application source code
COPY . .

# Run the Click CLI with the specified FUNCTION environment variable
CMD ["uvicorn", "sapientone.app:app", "--host", "0.0.0.0", "--port", "8080"]
