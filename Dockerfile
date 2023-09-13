FROM python:3.9

# Set the working directory
WORKDIR /app

# System dependencies
RUN apt-get update && \
    apt-get install -y llvm clang && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Python dependencies
RUN pip3 install llvmlite

# Copy local code to the container image
COPY . /app

ENTRYPOINT ["python3", "main.py"]
