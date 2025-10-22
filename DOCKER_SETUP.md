# Docker Setup Guide

## 🐳 Docker Installation

### For Ubuntu/Debian
```bash
# Update package index
sudo apt update

# Install Docker
sudo apt install docker.io

# Start Docker service
sudo systemctl start docker
sudo systemctl enable docker

# Add user to docker group (to run without sudo)
sudo usermod -aG docker $USER

# Log out and log back in for group changes to take effect
```

### For CentOS/RHEL
```bash
# Install Docker
sudo yum install docker

# Start Docker service
sudo systemctl start docker
sudo systemctl enable docker

# Add user to docker group
sudo usermod -aG docker $USER
```

### For macOS
Download and install Docker Desktop from [https://www.docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop)

### For Windows
Download and install Docker Desktop from [https://www.docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop)

## 🔧 Docker Verification

After installation, verify Docker is working:

```bash
# Check Docker version
docker --version

# Test Docker with hello-world
docker run hello-world
```

## 🚀 Quick Start with Enhanced System

### 1. Install Python Dependencies
```bash
# Install without oletools (compatible with Python 3.13)
pip install -r requirements_enhanced.txt
```

### 2. Start Docker Service
```bash
# On Linux systems
sudo systemctl start docker

# Or start manually if needed
sudo dockerd > /tmp/docker.log 2>&1 &
```

### 3. Run the Application
```bash
streamlit run enhanced_frontend.py
```

## 🔍 Troubleshooting

### Docker Permission Issues
If you get permission errors:
```bash
# Add your user to docker group
sudo usermod -aG docker $USER

# Log out and log back in, or run:
newgrp docker
```

### Docker Not Starting
If Docker service won't start:
```bash
# Check Docker status
sudo systemctl status docker

# Start Docker manually
sudo dockerd
```

### Port Conflicts
If port 8501 (Streamlit) is already in use:
```bash
# Kill existing Streamlit processes
pkill -f streamlit

# Or run on different port
streamlit run enhanced_frontend.py --server.port 8502
```

## 📋 System Requirements

- **Python**: 3.9+ (tested with 3.13)
- **Docker**: 20.10+
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 2GB free space

## 🛠️ Development Notes

- The system uses Docker to containerize generated applications
- Each Excel file generates a unique Docker container
- Containers are automatically managed and monitored
- Health checks ensure applications remain responsive

## 🔒 Security Considerations

- Generated applications run in isolated Docker containers
- No VBA macro execution (oletools removed for compatibility)
- Input validation prevents malicious file uploads
- Container resource limits prevent resource exhaustion