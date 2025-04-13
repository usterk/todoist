# Authentication System Documentation

This document provides detailed information about the Todoist API authentication system.

## Overview

The Todoist API supports two authentication methods:

1. **JWT Authentication**: Used for user sessions and direct API access
2. **API Key Authentication**: Used for external integrations or service accounts

All endpoints except for registration and login require authentication.

## User Registration

To create a new user account, use the registration endpoint:

### Endpoint

```
POST /api/auth/register
```

### Request Body

```json
{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "SecurePassword123"
}
```

### Requirements

- Username: 3-50 characters, must be unique
- Email: Valid email format, must be unique
- Password:
  - Minimum 8 characters long
  - Must contain at least one uppercase letter
  - Must contain at least one lowercase letter
  - Must contain at least one digit

### Response

**Success (201 Created):**

```json
{
  "id": 1,
  "username": "johndoe",
  "email": "john@example.com",
  "created_at": "2025-04-13T12:00:00"
}
```

**Error (400 Bad Request):**

If email is already registered:
```json
{
  "detail": "Email already registered"
}
```

If username is already taken:
```json
{
  "detail": "Username already taken"
}
```

**Error (422 Unprocessable Entity):**

If validation fails (example for password):
```json
{
  "detail": [
    {
      "loc": ["body", "password"],
      "msg": "Password must contain at least one uppercase letter",
      "type": "value_error"
    }
  ]
}
```

## User Login

After registration, users can log in to obtain a JWT token:

### Endpoint

```
POST /api/auth/login
```

### Request Body

```json
{
  "email": "john@example.com",
  "password": "SecurePassword123"
}
```

### Response

**Success (200 OK):**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com"
  }
}
```

**Error (401 Unauthorized):**

```json
{
  "detail": "Incorrect email or password"
}
```

## Using JWT Authentication

To authenticate requests using JWT:

1. Obtain a token using the login endpoint
2. Include the token in the Authorization header of your requests:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### JWT Token Structure

The JWT token consists of three parts:
- Header (algorithm and token type)
- Payload (claims)
- Signature

Our JWT payload includes:
- `sub`: Subject (user ID)
- `exp`: Expiration timestamp

JWT tokens expire after 30 minutes by default.

## API Key Management

API keys provide an alternative authentication method that doesn't expire like JWT tokens. They're useful for integrations, service accounts, or automated scripts.

### Generating an API Key

To generate a new API key:

#### Endpoint

```
POST /api/auth/apikey/generate
```

#### Requirements
- Must be authenticated with JWT token
- Optional description can be provided

#### Request Body

```json
{
  "description": "Integration for Project X"
}
```

#### Response

**Success (201 Created):**

```json
{
  "id": 1,
  "key_value": "j7HgTkOnM2lPqSw5xR8zD9vF3bY6cA1e",
  "description": "Integration for Project X",
  "created_at": "2025-04-13T14:30:00"
}
```

**Error (401 Unauthorized):**

```json
{
  "detail": "Not authenticated"
}
```

### Revoking an API Key

If an API key is compromised or no longer needed, it can be revoked:

#### Endpoint

```
POST /api/auth/apikey/revoke/{key_id}
```

#### Requirements
- Must be authenticated with JWT token
- Can only revoke your own API keys

#### Response

**Success (200 OK):**

```json
{
  "message": "API key successfully revoked"
}
```

**Error (404 Not Found):**

```json
{
  "detail": "API key not found"
}
```

### Using API Key Authentication

Include the API key in the x-api-key header:

```
x-api-key: j7HgTkOnM2lPqSw5xR8zD9vF3bY6cA1e
```

**Note:** Once revoked, an API key cannot be used for authentication.

## Authentication Middleware

All protected endpoints in the API use authentication middleware that:

1. Checks for a valid JWT token in the Authorization header
2. If JWT token is absent or invalid, checks for a valid API key
3. Returns 401 Unauthorized if no valid authentication is provided

## Error Responses

Authentication-related errors return appropriate HTTP status codes:

- **400 Bad Request**: Invalid input data
- **401 Unauthorized**: Authentication failed (invalid/missing token or API key)
- **403 Forbidden**: Valid authentication, but insufficient permissions
- **422 Unprocessable Entity**: Input validation failed

Each error response includes a detail field explaining the issue.

## Security Considerations

- Passwords are hashed using bcrypt with appropriate salt rounds
- JWT tokens are signed with a secure algorithm (HS256)
- JWT tokens have a limited expiration time
- API keys can be revoked if compromised
- Revoked API keys cannot be reactivated for security reasons

## Future Enhancements

Planned features for the authentication system:

- Token refresh mechanism
- API key listing endpoint
- More granular API key permissions
- Role-based access control

For any technical issues or questions regarding authentication, please contact the development team.