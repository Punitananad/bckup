"""
API Key Authentication Middleware
Protects public customer-facing endpoints with API key validation
"""
import secrets
from django.http import JsonResponse
from django.conf import settings
import logging

logger = logging.getLogger('api_security')


class APIKeyMiddleware:
    """
    Middleware to validate API keys for public endpoints.
    
    - Protects customer-facing API endpoints
    - Skips webhooks (they use signature verification)
    - Skips authenticated users (theatre staff)
    - Logs failed authentication attempts
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        # Load API key once at startup (not on every request for performance)
        self.api_key = getattr(settings, 'API_KEY', None)
        
        # Log initialization for debugging
        logger.warning(f"[MIDDLEWARE INIT] APIKeyMiddleware initialized with API_KEY: {self.api_key[:10] if self.api_key else 'NONE'}...")
        
        if not self.api_key:
            logger.error("[MIDDLEWARE INIT] API_KEY not configured!")
            raise Exception(
                "API_KEY not configured in settings. "
                "Please set API_KEY environment variable."
            )
        
        if self.api_key.startswith('CHANGE_THIS'):
            logger.error("[MIDDLEWARE INIT] API_KEY is still default value!")
            raise Exception(
                "API_KEY is still set to default value. "
                "Please set a real API_KEY in environment variable."
            )
    
    def __call__(self, request):
        # DEBUG: Log every request to verify middleware is running
        logger.info(f"[MIDDLEWARE] Processing: {request.method} {request.path}")
        
        # Check if this endpoint needs API key protection
        needs_key = self.needs_api_key(request)
        logger.info(f"[MIDDLEWARE] Needs API key: {needs_key}")
        
        if needs_key:
            # Check if user is already logged in (theatre staff)
            if request.user.is_authenticated:
                # Let them through - they're authenticated staff
                logger.info(f"[MIDDLEWARE] User authenticated, allowing access")
                return self.get_response(request)
            
            # Get the API key from request header
            provided_key = request.headers.get('X-API-Key', '')
            logger.info(f"[MIDDLEWARE] API key provided: {bool(provided_key)}")
            
            # Check if it matches (using constant-time comparison for security)
            if not provided_key or not secrets.compare_digest(provided_key, self.api_key):
                # Log the failed attempt for security monitoring
                logger.warning(
                    f"API key validation failed - "
                    f"IP: {self.get_client_ip(request)}, "
                    f"Path: {request.path}, "
                    f"Method: {request.method}, "
                    f"Key: {provided_key[:8] if provided_key else 'MISSING'}..."
                )
                
                # Reject the request with 401 Unauthorized
                return JsonResponse(
                    {
                        'error': 'Invalid or missing API key',
                        'status': 401
                    },
                    status=401
                )
            
            logger.info(f"[MIDDLEWARE] API key valid, allowing access")
        
        # All good - let the request through
        return self.get_response(request)
    
    def needs_api_key(self, request):
        """
        Determine which endpoints need API key validation.
        
        Returns True if the endpoint should be protected with API key.
        """
        path = request.path
        
        # SKIP these endpoints (don't need API key):
        skip_patterns = [
            '/admin/',              # Django admin panel
            '/static/',             # Static files (CSS, JS, images)
            '/media/',              # Media files (uploads)
            '/login',               # Login page
            '/logout',              # Logout
        ]
        
        for pattern in skip_patterns:
            if path.startswith(pattern):
                return False
        
        # SKIP all webhook endpoints (they use signature verification)
        if 'webhook' in path.lower():
            return False
        
        # PROTECT these public customer-facing API endpoints:
        public_api_patterns = [
            '/theatre/api/all-menu/',
            '/theatre/api/create-order',
            '/theatre/api/theatre-detail',
            '/theatre/api/tax-list/',
            '/theatre/api/order-data/',
            '/theatre/api/seat-last-order/',
            '/theatre/api/get-payu-form-details/',
            '/theatre/show-menu/',
            '/theatre/order-status/',
            '/theatre/order-feedback/',
        ]
        
        for pattern in public_api_patterns:
            if path.startswith(pattern):
                return True
        
        # Default: don't require API key
        return False
    
    def get_client_ip(self, request):
        """
        Get the real client IP address, handling proxies.
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            # Take the first IP in the chain
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', 'UNKNOWN')
        return ip
