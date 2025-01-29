# app/Dockerfile

FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy the project files into the container
COPY requirements.txt ./
COPY multilanguage_llm.py ./
COPY utils/ utils/
COPY data/ data
COPY .env .env


# Install Python dependencies
RUN pip install --upgrade pip \
    && pip install -r requirements.txt
# Load environment variables from .env file
ENV $(cat .env | xargs)
# Expose the port Streamlit runs on
EXPOSE 8501

# Healthcheck to ensure the app is running
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Run the Streamlit app
ENTRYPOINT ["streamlit", "run", "multilanguage_llm.py", "--server.port=8501", "--server.address=0.0.0.0"]
