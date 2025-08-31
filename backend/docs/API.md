# Qodo Demo API Documentation

This document describes the API endpoints for the Qodo Demo application.

## Overview

The Qodo Demo API provides endpoints for multiplication, search, and health monitoring. This API demonstrates various features including:

- Basic arithmetic operations
- Search functionality
- Health monitoring
- Request logging
- Performance metrics

## Base URL

```
http://localhost:8000
```

## Authentication

Currently, no authentication is required for demo purposes.

## Endpoints

### Multiplication

#### POST /multiply

Multiplies two numbers together.

**Request Body:**
```json
{
  "a": 5,
  "b": 3
}
```

**Response:**
```json
{
  "result": 15
}
```

**Notes:**
- This endpoint demonstrates inefficient loop implementation
- Could be optimized with simple multiplication
- Used for demo purposes to show code review opportunities

### Search

#### POST /search

Performs a search operation with the given query.

**Request Body:**
```json
{
  "query": "search term",
  "limit": 10,
  "filters": {}
}
```

**Response:**
```json
{
  "query": "search term",
  "results": ["Result 1", "Result 2"],
  "total_count": 2
}
```

**Notes:**
- This is the main new feature in this PR
- Supports custom limits and filters
- Returns mock results for demo purposes

#### GET /search/simple

Simple search endpoint for quick queries.

**Query Parameters:**
- `query` (required): Search query string

**Response:**
```json
{
  "query": "search term",
  "results": ["Result for search term"]
}
```

### Health and Monitoring

#### GET /health

Returns the health status of the API.

**Response:**
```json
{
  "status": "ok",
  "timestamp": "2024-01-15T10:00:00Z"
}
```

#### GET /stats

Returns application statistics.

**Response:**
```json
{
  "endpoints": 6,
  "version": "1.0.0",
  "status": "healthy"
}
```

#### GET /docs-update

Returns documentation update status.

**Response:**
```json
{
  "docs": "updated",
  "version": "1.0.0"
}
```

## Error Handling

The API returns standard HTTP status codes:

- `200 OK`: Successful request
- `400 Bad Request`: Invalid request data
- `500 Internal Server Error`: Server error

Error responses include error details:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Query cannot be empty",
    "details": {
      "field": "query",
      "value": ""
    }
  }
}
```

## Rate Limiting

Currently, no rate limiting is implemented for demo purposes.

## Logging

The API logs all requests with timing information. Logs include:

- HTTP method and path
- Response status code
- Request duration
- Timestamp

## Performance Considerations

- The multiplication endpoint uses an inefficient loop implementation
- Search results are mocked and return quickly
- Database operations are simulated for demo purposes

## Future Enhancements

Planned improvements include:

- Database integration for real search
- Authentication and authorization
- Rate limiting
- Caching layer
- More comprehensive error handling

## Demo Notes

This API is designed to demonstrate:

1. **Large PR Review**: Many files with trivial changes
2. **Code Quality Issues**: Inefficient implementations for review
3. **Feature Addition**: New search functionality
4. **Documentation**: Comprehensive API documentation
5. **Testing**: Extensive test coverage

The inefficient multiplication loop and other minor issues are intentionally included to provide opportunities for code review suggestions.
