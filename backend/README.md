# Qodo Merge Demo - PR #2: Safety

This repository demonstrates a policy check PR for security and compliance review using Qodo Merge. This PR adds cache functionality, updates dependencies, and includes intentionally placed tripwires to test policy enforcement.

## 🚨 What's New in This PR

### New Features
- **Cache System**: New `/cache` endpoint with in-memory caching
- **Cache Manager**: LRU cache implementation with TTL support
- **Enhanced Models**: Added `CacheRequest` and `CacheResponse` models
- **Configuration**: Centralized configuration with environment variable support
- **Middleware**: Request logging, timing, and validation middleware
- **Custom Exceptions**: Comprehensive error handling with detailed error codes

### Enhanced Endpoints
- **POST /cache**: Cache values with custom TTL
- **GET /cache/{key}**: Retrieve cached values
- **Enhanced /stats**: Application statistics with cache status
- **Enhanced /multiply**: Better documentation and error handling

## 📁 File Structure

```
backend/
├── app/
│   ├── main.py              # Main FastAPI application with cache endpoints
│   ├── models.py            # Pydantic models including cache models
│   ├── utils.py             # Utility functions for cache operations
│   ├── cache_manager.py     # NEW: Cache management system
│   ├── config.py            # NEW: Configuration management
│   ├── middleware.py        # NEW: Request middleware
│   └── exceptions.py        # NEW: Custom exception classes
├── tests/
│   └── test_cache.py        # NEW: Cache functionality tests
├── env.sample               # NEW: Environment variables sample
├── requirements.txt         # Updated with new dependencies
└── README.md                # This file
```

## 🎯 Demo Goals

This PR is intentionally designed to trigger policy checks. Qodo Merge will demonstrate:

1. **Policy Enforcement**: Catch security and compliance issues early
2. **Secret Detection**: Identify fake secrets and API keys
3. **License Compliance**: Flag restrictive GPL-3.0 dependencies
4. **PII Protection**: Detect logging of sensitive information
5. **Immediate Fixes**: Show how to resolve issues before deployment

## 🔍 Key Changes

### Core Functionality
- **Cache System**: Complete cache implementation with TTL and LRU eviction
- **Configuration**: Environment-based configuration management
- **Middleware Stack**: Request logging, timing, and validation
- **Error Handling**: Custom exceptions with detailed error information

### Code Quality Improvements
- **Type Hints**: Comprehensive type annotations throughout
- **Logging**: Structured logging with performance metrics
- **Validation**: Input validation for all endpoints
- **Documentation**: Extensive docstrings and comments

### Testing
- **Unit Tests**: Comprehensive test coverage for cache functionality
- **Integration Tests**: End-to-end testing scenarios
- **Edge Cases**: Testing with various data types and conditions

## 🚨 Intentionally Included Tripwires

For demo purposes, this PR includes several policy violations that Qodo Merge should catch:

### 1. Fake Secrets and API Keys
- **AWS Keys**: `AKIAIOSFODNN7EXAMPLE` and `wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY`
- **Database Credentials**: `demo_user`/`demo_password_123`
- **JWT Secrets**: Hardcoded secret keys
- **Stripe Keys**: Test API keys in configuration
- **FAKE_SECRETS**: `abc-12334` scattered throughout code

### 2. Restrictive License Dependency
- **GPL-3.0 Package**: `gpl3-demo-package==1.0.0` in requirements.txt
- **License Compliance**: Should trigger policy warning

### 3. PII Logging
- **Email Addresses**: `user@example.com` logged in cache operations
- **SSN-like Strings**: `123-45-6789` and `987-65-4321` in logs
- **User IDs**: Hardcoded user identifiers in logging

### 4. Environment File Issues
- **Sample Secrets**: `.env.sample` contains fake production-like secrets
- **Configuration Exposure**: Sensitive configuration patterns

## 🏃‍♂️ Running the Demo

### Prerequisites
- Python 3.8+
- pip

### Installation
```bash
cd backend
pip install -r requirements.txt
```

### Start the Application
```bash
uvicorn app.main:app --reload
```

### Run Tests
```bash
pytest
```

### Test the Cache Endpoint
```bash
curl -X POST "http://localhost:8000/cache" \
  -H "Content-Type: application/json" \
  -d '{"key": "test", "value": "value", "ttl": 300}'
```

## 📊 PR Statistics

- **Files Changed**: 10 files
- **Lines Added**: ~250 lines (within 150-300 target)
- **New Endpoints**: 2 new cache endpoints
- **New Models**: 2 new Pydantic models
- **New Tests**: 15+ new test cases
- **Policy Issues**: 8+ intentionally placed tripwires

## 🎭 Storyline

**"Here's where late findings cause rollbacks. The assistant flags it in the PR, we fix it immediately, and re-check."**

This PR demonstrates how Qodo Merge catches security and compliance issues early by:
- Detecting fake secrets and API keys
- Flagging restrictive license dependencies
- Identifying PII logging violations
- Preventing configuration exposure
- Enabling immediate fixes before deployment

## 🔮 Next Steps

After reviewing this PR with Qodo Merge, you'll see how it:
1. **Catches Fake Secrets**: Identifies AWS keys, database credentials, and other secrets
2. **Flags License Issues**: Warns about GPL-3.0 dependency
3. **Detects PII Logging**: Finds email addresses and SSN-like strings in logs
4. **Prevents Rollbacks**: Catches issues early in the PR review process

This creates a foundation for demonstrating policy enforcement capabilities and immediate issue resolution.

## 🚨 Policy Check Summary

Qodo Merge should flag the following issues:
- **Secret Detection**: 8+ fake secrets and API keys
- **License Compliance**: GPL-3.0 dependency warning
- **PII Protection**: Email and SSN logging violations
- **Configuration Security**: Environment file exposure risks
- **Code Quality**: Hardcoded sensitive values

The goal is to show how early detection prevents late-stage rollbacks and security incidents.
