# MetaHuman FBX to GLB Converter Docker Image
FROM python:3.10-slim-bullseye

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONPATH=/app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    # Build tools
    build-essential \
    cmake \
    git \
    wget \
    curl \
    unzip \
    # Graphics libraries
    libgl1-mesa-glx \
    libglib2.0-0 \
    # X11 libraries for headless operations
    xvfb \
    # FBX dependencies
    libxml2 \
    libxml2-dev \
    zlib1g-dev \
    # Python dev tools
    python3-dev \
    # Clean up
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Create a non-root user
RUN groupadd -r fbx && useradd -r -g fbx -m -d /home/fbx fbx

# Copy requirements first for better caching
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Install FBX SDK dependencies (using community solutions)
RUN pip install --no-cache-dir \
    # Core dependencies from requirements.txt
    "pygltflib>=1.16.0" \
    "Pillow>=10.0.0" \
    "click>=8.1.0" \
    "rich>=13.0.0" \
    "pytest>=7.4.0" \
    "pytest-cov>=4.1.0" \
    # Additional dependencies for FBX processing
    "numpy>=1.24.0" \
    "scipy>=1.10.0" \
    # Alternative FBX libraries
    "lxml>=4.9.0" \
    # Binary tools
    "blender-bpy>=3.6.0" || echo "Blender BPY not available, continuing..."

# Try to install FBX SDK Python bindings for Python 3.10 (if available)
RUN pip install --no-cache-dir \
    "https://github.com/3DTech-Steven7/python-fbx/raw/master/Python310_x64/fbx/fbx.pyd" || \
    echo "Official FBX SDK not available, using alternative parsers"

# Download and install FBX2glTF tool (optional - continue if not available)
RUN wget -O /tmp/fbx2gltf.tar.gz \
    "https://github.com/facebookincubator/FBX2glTF/releases/download/v0.13.1/FBX2glTF-linux-x64.tar.gz" && \
    tar -xzf /tmp/fbx2gltf.tar.gz -C /usr/local/bin/ && \
    chmod +x /usr/local/bin/FBX2glTF && \
    rm /tmp/fbx2gltf.tar.gz || \
    echo "FBX2glTF download failed, continuing without it"

# Download and install gltf-transform
RUN npm_installed=false && \
    (curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
     apt-get install -y nodejs && \
     npm install -g @gltf-transform/cli && \
     npm_installed=true) || \
    echo "Node.js/gltf-transform installation failed, using Python alternatives"

# Copy application code
COPY . /app/

# Create necessary directories
RUN mkdir -p /app/input /app/output /app/temp && \
    chown -R fbx:fbx /app

# Install the package in development mode
RUN pip install --no-cache-dir -e .

# Set up the entry point script
RUN echo '#!/bin/bash\n\
# MetaHuman FBX to GLB Converter Entry Point\n\
\n\
# Set up virtual display for headless operation\n\
export DISPLAY=:99\n\
Xvfb :99 -screen 0 1024x768x24 > /dev/null 2>&1 &\n\
\n\
# Ensure proper permissions\n\
chown -R fbx:fbx /app/input /app/output /app/temp 2>/dev/null || true\n\
\n\
# Run the application\n\
exec "$@"\n\
' > /app/entrypoint.sh && \
chmod +x /app/entrypoint.sh

# Switch to non-root user
USER fbx

# Set up the working directories
VOLUME ["/app/input", "/app/output", "/app/temp"]

# Expose port for any web interface (if added later)
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "from metahuman_converter.validation import validate_fbx; print('OK')" || exit 1

# Default command
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["python", "example_usage.py"] 