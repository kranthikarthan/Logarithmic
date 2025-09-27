# Installation Guide

## Quick Start (Recommended)

### Option 1: Using Docker (Easiest)

1. **Install Docker** (if not already installed)
   - [Docker Desktop](https://www.docker.com/products/docker-desktop/) for Windows/Mac
   - Or install Docker on Linux: `sudo apt install docker.io`

2. **Run with Docker Compose**
   ```bash
   docker-compose up -d
   ```

3. **Access the application**
   - Open your browser to `http://localhost:5000`

### Option 2: Using Python Virtual Environment

1. **Make sure Python 3.7+ is installed**
   ```bash
   python3 --version
   ```

2. **Run the startup script**
   ```bash
   ./start.sh
   ```

3. **Access the application**
   - Open your browser to `http://localhost:5000`

### Option 3: Manual Installation

1. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python run.py
   ```

## Configuration

### Environment Variables

Create a `.env` file (optional):
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
HOST=0.0.0.0
PORT=5000
```

### Jira Setup

1. **Get your Jira API Token**:
   - Go to [Atlassian Account Settings](https://id.atlassian.com/manage-profile/security/api-tokens)
   - Click "Create API token"
   - Give it a name and copy the token

2. **Login to the application**:
   - Enter your Jira URL (e.g., `https://your-domain.atlassian.net`)
   - Enter your Jira username/email
   - Enter your API token

## Troubleshooting

### Common Issues

**"Module not found" errors**:
- Make sure you're in the virtual environment: `source venv/bin/activate`
- Reinstall dependencies: `pip install -r requirements.txt`

**"Port already in use"**:
- Change the port: `export PORT=5001 && python run.py`
- Or kill the process using port 5000

**"Permission denied" on startup script**:
- Make it executable: `chmod +x start.sh`

**Docker issues**:
- Make sure Docker is running
- Try: `docker-compose down && docker-compose up --build`

### Getting Help

1. Check the logs for error messages
2. Verify your Jira credentials
3. Ensure your Jira account has the necessary permissions
4. Check the README.md for more details

## Production Deployment

For production use:

1. **Set a strong secret key**:
   ```env
   SECRET_KEY=your-very-secure-secret-key-here
   ```

2. **Disable debug mode**:
   ```env
   DEBUG=False
   ```

3. **Use a reverse proxy** (nginx, Apache) for better security

4. **Set up SSL/HTTPS** for secure connections

5. **Use environment variables** for configuration instead of .env files