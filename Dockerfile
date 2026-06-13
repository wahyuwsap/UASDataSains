# Base image 
FROM python:3.12-slim 

# Set working directory 
WORKDIR /app 

# Copy requirements 
COPY requirements.txt . 

# Install dependencies 
RUN pip install --no-cache-dir -r requirements.txt 

# Copy all files ke container 
COPY . . 

# Expose port untuk Hugging Face Spaces 
EXPOSE 7860 

# Run Flask 
CMD ["gunicorn", "-b", "0.0.0.0:7860", "app:app"]