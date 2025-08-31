# Qodo Demo Setup Guide

This document provides setup instructions for the Qodo Demo application.

## Prerequisites

Before setting up the Qodo Demo application, ensure you have the following installed:

- Python 3.8 or higher
- pip (Python package installer)
- Git (for version control)

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd testing-qodo/backend
```

### 2. Create Virtual Environment

It's recommended to use a virtual environment to isolate dependencies:

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

Install the required Python packages:

```bash
pip install -r requirements.txt
```

### 4. Verify Installation

Check that all dependencies are installed correctly:

```bash
python -c "import fastapi, pydantic, pytest; print('All dependencies installed successfully!')"
```

## Configuration

### Environment Variables

The application can be configured using environment variables:

```bash
# Database configuration
export DATABASE_URL="sqlite:///demo.db"

# Application settings
export DEBUG="false"
export LOG_LEVEL="INFO"

# API settings
export API_PREFIX="/api/v1"
export CORS_ORIGINS="*"
export RATE_LIMIT="100"
```

### Configuration File

You can also create a `.env` file in the project root:

```env
DATABASE_URL=sqlite:///demo.db
DEBUG=false
LOG_LEVEL=INFO
API_PREFIX=/api/v1
CORS_ORIGINS=*
RATE_LIMIT=100
```

## Running the Application

### Development Mode

Start the application in development mode with auto-reload:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode

For production deployment:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Using Docker

If you prefer Docker:

```bash
# Build the image
docker build -t qodo-demo .

# Run the container
docker run -p 8000:8000 qodo-demo
```

## Testing

### Run All Tests

Execute the test suite:

```bash
pytest
```

### Run Specific Test Files

Run tests for specific modules:

```bash
# Run search tests
pytest tests/test_search.py

# Run utility tests
pytest tests/test_utils.py

# Run with verbose output
pytest -v
```

### Run Tests with Coverage

Generate coverage reports:

```bash
pytest --cov=app --cov-report=html
```

### Run Tests in Parallel

For faster test execution:

```bash
pytest -n auto
```

## Database Setup

### SQLite Database

The application uses SQLite by default:

```bash
# Database will be created automatically on first run
# Location: backend/demo.db
```

### Custom Database

To use a different database:

1. Update the `DATABASE_URL` environment variable
2. Install appropriate database drivers
3. Update database connection logic in `app/database.py`

## Logging

### Log Levels

Configure logging verbosity:

- `DEBUG`: Detailed information for debugging
- `INFO`: General information about application flow
- `WARNING`: Warning messages for potential issues
- `ERROR`: Error messages for failed operations
- `CRITICAL`: Critical errors that may cause application failure

### Log Format

Logs include:
- Timestamp
- Log level
- Module name
- Message
- Additional context

## Monitoring

### Health Checks

Monitor application health:

```bash
curl http://localhost:8000/health
```

### Statistics

View application statistics:

```bash
curl http://localhost:8000/stats
```

### Metrics

The application provides various metrics:
- Request counts
- Response times
- Error rates
- Search query statistics

## Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   # Find process using port 8000
   lsof -i :8000
   
   # Kill the process
   kill -9 <PID>
   ```

2. **Import Errors**
   ```bash
   # Ensure virtual environment is activated
   source venv/bin/activate
   
   # Reinstall dependencies
   pip install -r requirements.txt
   ```

3. **Database Errors**
   ```bash
   # Remove existing database
   rm demo.db
   
   # Restart application
   ```

### Debug Mode

Enable debug mode for detailed error information:

```bash
export DEBUG=true
uvicorn app.main:app --reload
```

## Development

### Code Style

Follow PEP 8 guidelines:

```bash
# Install flake8
pip install flake8

# Check code style
flake8 app/ tests/
```

### Type Checking

Use mypy for type checking:

```bash
# Install mypy
pip install mypy

# Check types
mypy app/
```

### Pre-commit Hooks

Set up pre-commit hooks:

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install
```

## Deployment

### Production Considerations

- Use a production WSGI server (Gunicorn, uWSGI)
- Set up reverse proxy (Nginx, Apache)
- Configure SSL/TLS certificates
- Set up monitoring and alerting
- Use environment-specific configuration
- Implement proper logging and error handling

### Docker Deployment

```bash
# Build production image
docker build -f Dockerfile.prod -t qodo-demo:prod .

# Run with environment variables
docker run -d \
  -p 8000:8000 \
  -e DATABASE_URL="postgresql://user:pass@host/db" \
  -e DEBUG="false" \
  qodo-demo:prod
```

## Support

For issues and questions:

1. Check the troubleshooting section
2. Review application logs
3. Check GitHub issues
4. Contact the development team

## Demo Notes

This setup guide demonstrates:

1. **Comprehensive Documentation**: Detailed setup instructions
2. **Multiple Configuration Options**: Environment variables, config files
3. **Testing Setup**: Various testing approaches and tools
4. **Deployment Options**: Development and production configurations
5. **Troubleshooting**: Common issues and solutions

The guide is intentionally detailed to provide many small changes for the PR review demo.
