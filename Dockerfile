# Simple MetaHuman FBX Validator
FROM lscr.io/linuxserver/blender:4.4.3

# Switch to root to install Python dependencies
USER root

# Install Python and pip
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy and install Python requirements
COPY requirements.txt .
RUN pip3 install --no-cache-dir --break-system-packages -r requirements.txt

# Copy application code
COPY metahuman_converter/ ./metahuman_converter/
COPY validate.py .

# Switch back to the linuxserver user
USER abc

# Default command - validate input-file.fbx  
CMD ["python3", "validate.py"] 