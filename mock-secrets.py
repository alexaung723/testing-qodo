# Mock Secrets File - For Testing Policy Checks Only
# DO NOT use these in production - they are intentionally fake for demo purposes

# AWS Access Keys
AWS_ACCESS_KEY_ID = "AKIAIOSFODNN7EXAMPLE"
AWS_SECRET_ACCESS_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
AWS_SESSION_TOKEN = "AQoEXAMPLEH4aoAH0gNCAPyJxz4BlCFFxWNE1OPTgk5TthT+vwEny2mLd0aKkfn14Yw5kbAXMLojEfgn49IU5We8ID8iL4B3ty3ZbkJshqqENy2ft8VBKtPOQqMQ5kozyt"

# Database Credentials
DB_USERNAME = "admin_user"
DB_PASSWORD = "SuperSecretPassword123!"
DB_HOST = "prod-database.cluster.region.rds.amazonaws.com"
DB_PORT = "5432"
DB_NAME = "production_db"

# API Keys
STRIPE_SECRET_KEY = "sk_test_51H1234567890abcdefghijklmnopqrstuvwxyz"
STRIPE_PUBLISHABLE_KEY = "pk_test_51H1234567890abcdefghijklmnopqrstuvwxyz"
GOOGLE_API_KEY = "AIzaSyC1m0U8XNoExampleKey123456789"
TWILIO_AUTH_TOKEN = "1234567890abcdef1234567890abcdef"
SENDGRID_API_KEY = "SG.1234567890abcdefghijklmnopqrstuvwxyz.1234567890abcdefghijklmnopqrstuvwxyz"

# JWT and Encryption
JWT_SECRET_KEY = "my-super-secret-jwt-key-that-should-be-very-long-and-random-12345"
ENCRYPTION_KEY = "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6"
BCRYPT_SALT = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/vHhHq"

# Redis and Cache
REDIS_PASSWORD = "redis_password_123"
REDIS_HOST = "cache.redis.amazonaws.com"
REDIS_PORT = "6379"
REDIS_DB = "0"

# Email Configuration
SMTP_USERNAME = "noreply@company.com"
SMTP_PASSWORD = "email_password_123"
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = "587"

# OAuth Credentials
GITHUB_CLIENT_SECRET = "ghp_1234567890abcdefghijklmnopqrstuvwxyz"
GOOGLE_CLIENT_SECRET = "GOCSPX-1234567890abcdefghijklmnopqrstuvwxyz"
FACEBOOK_APP_SECRET = "1234567890abcdef1234567890abcdef"

# SSH Keys
SSH_PRIVATE_KEY = """-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAlwAAAAdzc2gtcn
NhAAAAAwEAAQAAAQEA1234567890abcdefghijklmnopqrstuvwxyz
-----END OPENSSH PRIVATE KEY-----"""

# Docker Registry
DOCKER_REGISTRY_PASSWORD = "docker_registry_password_123"
DOCKER_REGISTRY_URL = "registry.docker.io"
DOCKER_REGISTRY_USERNAME = "docker_user"

# Kubernetes
KUBECONFIG_CONTENT = """apiVersion: v1
kind: Config
clusters:
- name: production-cluster
  cluster:
    server: https://kubernetes.example.com
    certificate-authority-data: LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCg==
users:
- name: admin-user
  user:
    token: eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.example.token.here"""

# Cloud Provider Secrets
AZURE_CLIENT_SECRET = "azure_client_secret_123"
AZURE_TENANT_ID = "12345678-1234-1234-1234-123456789012"
GCP_SERVICE_ACCOUNT_KEY = "gcp_service_account_key_123"

# Monitoring and Logging
DATADOG_API_KEY = "1234567890abcdef1234567890abcdef"
NEW_RELIC_LICENSE_KEY = "new_relic_license_key_123"
SENTRY_DSN = "https://1234567890abcdef1234567890abcdef@o123456.ingest.sentry.io/123456"

# Payment Processing
PAYPAL_CLIENT_SECRET = "paypal_client_secret_123"
SQUARE_ACCESS_TOKEN = "square_access_token_123"
STRIPE_WEBHOOK_SECRET = "whsec_1234567890abcdefghijklmnopqrstuvwxyz"

# Social Media
TWITTER_API_SECRET = "twitter_api_secret_123"
LINKEDIN_CLIENT_SECRET = "linkedin_client_secret_123"
INSTAGRAM_ACCESS_TOKEN = "instagram_access_token_123"

# File Storage
S3_BUCKET_NAME = "my-production-bucket"
S3_ACCESS_KEY = "AKIAIOSFODNN7EXAMPLE"
S3_SECRET_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"

# Database Connection Strings
POSTGRES_CONNECTION = "postgresql://admin_user:SuperSecretPassword123!@prod-database.cluster.region.rds.amazonaws.com:5432/production_db"
MONGODB_CONNECTION = "mongodb://admin_user:SuperSecretPassword123!@prod-mongodb.cluster.region.mongodb.net:27017/production_db"
REDIS_CONNECTION = "redis://:redis_password_123@cache.redis.amazonaws.com:6379/0"

# Environment Variables
ENV_VARS = {
    "NODE_ENV": "production",
    "SECRET_KEY": "my-super-secret-key-that-should-be-very-long-and-random-12345",
    "DATABASE_URL": "postgresql://admin_user:SuperSecretPassword123!@prod-database.cluster.region.rds.amazonaws.com:5432/production_db",
    "REDIS_URL": "redis://:redis_password_123@cache.redis.amazonaws.com:6379/0",
    "JWT_SECRET": "my-super-secret-jwt-key-that-should-be-very-long-and-random-12345"
}

# Test Data with PII (for policy check testing)
TEST_USERS = [
    {"email": "user1@example.com", "ssn": "123-45-6789", "phone": "+1-555-123-4567"},
    {"email": "user2@example.com", "ssn": "987-65-4321", "phone": "+1-555-987-6543"},
    {"email": "admin@company.com", "ssn": "111-22-3333", "phone": "+1-555-111-2222"}
]

# FAKE_SECRETS=abc-12334  # This should be caught by policy checks
