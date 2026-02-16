# Requirements Document

## Introduction

This document specifies the requirements for implementing API endpoint security to protect against unauthorized access from a former developer who has knowledge of all current endpoint URLs and system structure. The solution will implement API key authentication middleware for public customer-facing endpoints while preserving existing authentication mechanisms for webhooks and authenticated theatre staff.

## Glossary

- **API_Key_Middleware**: Django middleware component that validates API key headers on incoming requests
- **Public_Endpoint**: Customer-facing API endpoints that currently have no authentication (menu, ordering, theatre details)
- **Webhook_Endpoint**: Payment gateway callback endpoints that use signature verification (Razorpay, PayU, PhonePe, CCAvenue, Cashfree)
- **Protected_Endpoint**: Endpoints that require Django authentication (theatre staff operations)
- **API_Key**: A secure random string used to authenticate API requests via HTTP header
- **X-API-Key**: Standard HTTP header name for transmitting the API key
- **Environment_Variable**: Configuration value stored in .env file and accessed via os.environ

## Requirements

### Requirement 1: API Key Authentication Middleware

**User Story:** As a system administrator, I want to implement API key authentication middleware, so that only authorized clients can access public API endpoints.

#### Acceptance Criteria

1. THE API_Key_Middleware SHALL validate the presence of an X-API-Key header on all incoming requests to Public_Endpoints
2. WHEN a request contains a valid API key, THE API_Key_Middleware SHALL allow the request to proceed to the view
3. WHEN a request contains an invalid API key, THE API_Key_Middleware SHALL return HTTP 401 Unauthorized with error message "Invalid or missing API key"
4. WHEN a request is missing the X-API-Key header, THE API_Key_Middleware SHALL return HTTP 401 Unauthorized with error message "Invalid or missing API key"
5. THE API_Key_Middleware SHALL read the expected API key value from the API_KEY environment variable
6. WHEN the API_KEY environment variable is not set, THE API_Key_Middleware SHALL raise an ImproperlyConfigured exception at startup

### Requirement 2: Selective Endpoint Protection

**User Story:** As a system administrator, I want the middleware to selectively protect endpoints, so that webhooks and authenticated requests continue to work without API keys.

#### Acceptance Criteria

1. THE API_Key_Middleware SHALL NOT apply to requests matching URL pattern `/theatre/api/.*webhook.*`
2. THE API_Key_Middleware SHALL NOT apply to requests matching URL pattern `/admin/.*`
3. THE API_Key_Middleware SHALL NOT apply to requests for static files matching URL pattern `/static/.*`
4. THE API_Key_Middleware SHALL NOT apply to requests for media files matching URL pattern `/media/.*`
5. WHEN a request has a valid Django session (request.user.is_authenticated is True), THE API_Key_Middleware SHALL allow the request to proceed without checking the API key
6. THE API_Key_Middleware SHALL apply to all requests matching URL pattern `/theatre/api/.*` that are not excluded by other criteria
7. THE API_Key_Middleware SHALL apply to requests to endpoints: all-menu, create-order, theatre-detail, tax-list, order-data, get-payu-form-details

### Requirement 3: Security Logging

**User Story:** As a security administrator, I want failed authentication attempts to be logged, so that I can monitor for potential security threats.

#### Acceptance Criteria

1. WHEN an API key validation fails, THE API_Key_Middleware SHALL log the failed attempt including timestamp, IP address, requested path, and provided API key (first 8 characters only)
2. WHEN an API key validation succeeds, THE API_Key_Middleware SHALL NOT log the request (to avoid log spam)
3. THE API_Key_Middleware SHALL use Python's logging module with logger name "api_security"
4. THE API_Key_Middleware SHALL log failed attempts at WARNING level

### Requirement 4: API Key Configuration

**User Story:** As a system administrator, I want to configure the API key via environment variables, so that I can easily rotate keys without code changes.

#### Acceptance Criteria

1. THE System SHALL read the API key from environment variable API_KEY
2. THE .env.template file SHALL include an API_KEY entry with a placeholder value
3. THE deployment documentation SHALL include instructions for generating a secure random API key of at least 32 characters
4. THE System SHALL support API key rotation by simply updating the environment variable and restarting the application
5. WHEN generating a new API key, THE System SHALL use cryptographically secure random generation (secrets module)

### Requirement 5: Frontend Integration

**User Story:** As a developer, I want the frontend to automatically include the API key in requests, so that customer orders continue to work seamlessly.

#### Acceptance Criteria

1. THE Django templates SHALL inject the API key into JavaScript context from Django settings
2. THE menu.js file SHALL include the X-API-Key header in all fetch/AJAX requests to API endpoints
3. WHEN making API requests, THE JavaScript code SHALL retrieve the API key from the template context (not hardcoded)
4. THE API key SHALL NOT be exposed in client-side JavaScript files that are publicly accessible
5. THE API key SHALL be rendered in Django templates using template variables that are only accessible to authenticated users or embedded in customer-facing pages

### Requirement 6: Error Handling and Response Format

**User Story:** As a frontend developer, I want consistent error responses, so that I can handle authentication failures gracefully.

#### Acceptance Criteria

1. WHEN API key validation fails, THE API_Key_Middleware SHALL return a JSON response with format: {"error": "Invalid or missing API key", "status": 401}
2. THE API_Key_Middleware SHALL set the Content-Type header to "application/json" for error responses
3. THE API_Key_Middleware SHALL return HTTP status code 401 for authentication failures
4. THE error response SHALL NOT reveal any information about the expected API key format or value

### Requirement 7: Performance and Efficiency

**User Story:** As a system administrator, I want the middleware to have minimal performance impact, so that customer experience is not degraded.

#### Acceptance Criteria

1. THE API_Key_Middleware SHALL perform API key validation using constant-time comparison (secrets.compare_digest)
2. THE API_Key_Middleware SHALL cache the expected API key value in memory (not read from environment on every request)
3. THE API_Key_Middleware SHALL execute URL pattern matching before API key validation to skip unnecessary checks
4. THE middleware execution time SHALL add less than 5ms to request processing time for protected endpoints

### Requirement 8: Backward Compatibility

**User Story:** As a system administrator, I want to ensure existing functionality is not broken, so that theatre operations continue without disruption.

#### Acceptance Criteria

1. WHEN the middleware is deployed, THE webhook endpoints SHALL continue to process payment callbacks using existing signature verification
2. WHEN the middleware is deployed, THE authenticated theatre staff SHALL continue to access protected endpoints using Django session authentication
3. WHEN the middleware is deployed, THE Django admin interface SHALL remain accessible without API keys
4. THE middleware SHALL NOT modify request or response objects except when returning authentication errors

### Requirement 9: Documentation and Deployment

**User Story:** As a deployment engineer, I want clear documentation, so that I can deploy the security changes safely.

#### Acceptance Criteria

1. THE deployment guide SHALL include step-by-step instructions for generating and configuring the API key
2. THE deployment guide SHALL include a checklist of all files that need to be updated
3. THE deployment guide SHALL include instructions for testing the API key authentication before going live
4. THE deployment guide SHALL include rollback procedures in case of issues
5. THE deployment guide SHALL include instructions for rotating the API key in production

### Requirement 10: Optional URL Prefix Versioning

**User Story:** As a system administrator, I want the option to add URL prefixes, so that I can further obscure endpoint locations from the former developer.

#### Acceptance Criteria

1. WHERE URL prefix versioning is enabled, THE System SHALL support a configurable URL prefix via environment variable API_URL_PREFIX
2. WHERE URL prefix versioning is enabled, THE System SHALL accept requests to both `/theatre/api/` and `/{API_URL_PREFIX}/api/` patterns
3. WHERE URL prefix versioning is enabled, THE frontend code SHALL use the configured prefix for all API requests
4. WHERE URL prefix versioning is enabled, THE middleware SHALL validate API keys for requests matching the new prefix pattern
5. THE URL prefix feature SHALL be optional and disabled by default (empty string)
