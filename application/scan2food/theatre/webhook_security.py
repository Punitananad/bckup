"""
Webhook Security Utilities
Provides signature verification for ALL payment gateway webhooks
"""

import hmac
import hashlib
import os
import base64


# ============================================================================
# RAZORPAY WEBHOOK VERIFICATION
# ============================================================================

def verify_razorpay_webhook_signature(payload_body, signature, webhook_secret):
    """
    Verify Razorpay webhook signature
    
    Args:
        payload_body (bytes): Raw request body
        signature (str): X-Razorpay-Signature header value
        webhook_secret (str): Webhook secret from Razorpay dashboard
    
    Returns:
        bool: True if signature is valid, False otherwise
    """
    if not webhook_secret:
        print("WARNING: No webhook secret configured for Razorpay")
        return True  # Backward compatibility
    
    try:
        # Generate expected signature
        expected_signature = hmac.new(
            webhook_secret.encode('utf-8'),
            payload_body,
            hashlib.sha256
        ).hexdigest()
        
        # Compare signatures (constant-time comparison)
        return hmac.compare_digest(expected_signature, signature)
        
    except Exception as e:
        print(f"Error verifying Razorpay webhook signature: {e}")
        return False


# ============================================================================
# PAYU WEBHOOK VERIFICATION
# ============================================================================

def verify_payu_webhook_hash(post_data, gateway_salt):
    """
    Verify PayU webhook hash
    
    Args:
        post_data (dict): POST data from PayU webhook
        gateway_salt (str): Gateway salt from database
    
    Returns:
        tuple: (is_valid, error_message)
    """
    if not gateway_salt:
        print("WARNING: No gateway salt configured for PayU")
        return True, None  # Backward compatibility
    
    try:
        # Extract data from POST
        status = post_data.get('status', '')
        key = post_data.get('key', '')
        txnid = post_data.get('txnid', '')
        amount = post_data.get('amount', '')
        productinfo = post_data.get('productinfo', '')
        firstname = post_data.get('firstname', '')
        email = post_data.get('email', '')
        udf1 = post_data.get('udf1', '')
        udf2 = post_data.get('udf2', '')
        udf3 = post_data.get('udf3', '')
        udf4 = post_data.get('udf4', '')
        udf5 = post_data.get('udf5', '')
        received_hash = post_data.get('hash', '')
        
        # PayU hash formula (reverse order for response)
        # salt|status||||||udf5|udf4|udf3|udf2|udf1|email|firstname|productinfo|amount|txnid|key
        hash_string = f"{gateway_salt}|{status}||||||{udf5}|{udf4}|{udf3}|{udf2}|{udf1}|{email}|{firstname}|{productinfo}|{amount}|{txnid}|{key}"
        
        # Calculate expected hash
        expected_hash = hashlib.sha512(hash_string.encode('utf-8')).hexdigest()
        
        # Compare hashes
        if hmac.compare_digest(expected_hash.lower(), received_hash.lower()):
            return True, None
        else:
            return False, "Hash mismatch"
            
    except Exception as e:
        print(f"Error verifying PayU webhook hash: {e}")
        return False, str(e)


# ============================================================================
# PHONEPE WEBHOOK VERIFICATION
# ============================================================================

def verify_phonepe_webhook_signature(payload_body, signature, salt_key, salt_index=1):
    """
    Verify PhonePe webhook signature (X-VERIFY header)
    
    Args:
        payload_body (bytes): Raw request body
        signature (str): X-VERIFY header value
        salt_key (str): Gateway secret (salt key)
        salt_index (int): Salt index (default 1)
    
    Returns:
        tuple: (is_valid, error_message)
    """
    if not salt_key:
        print("WARNING: No salt key configured for PhonePe")
        return True, None  # Backward compatibility
    
    try:
        # PhonePe signature formula: Base64(SHA256(response + salt_key + salt_index))
        payload_str = payload_body.decode('utf-8') if isinstance(payload_body, bytes) else payload_body
        
        # Create string to hash
        string_to_hash = f"{payload_str}{salt_key}{salt_index}"
        
        # Calculate SHA256
        sha256_hash = hashlib.sha256(string_to_hash.encode('utf-8')).digest()
        
        # Base64 encode
        expected_signature = base64.b64encode(sha256_hash).decode('utf-8')
        
        # Compare signatures
        if hmac.compare_digest(expected_signature, signature):
            return True, None
        else:
            return False, "Signature mismatch"
            
    except Exception as e:
        print(f"Error verifying PhonePe webhook signature: {e}")
        return False, str(e)


# ============================================================================
# CCAVENUE WEBHOOK VALIDATION
# ============================================================================

def validate_ccavenue_webhook(payment_data, order):
    """
    Validate CCAvenue webhook data
    
    Args:
        payment_data (dict): Decrypted payment data
        order: Order object from database
    
    Returns:
        tuple: (is_valid, error_message)
    """
    try:
        # Validate order_id format
        order_id = payment_data.get('order_id')
        if not order_id:
            return False, "Missing order_id"
        
        # Validate order_status
        order_status = payment_data.get('order_status')
        if not order_status:
            return False, "Missing order_status"
        
        # Validate amount (if order exists)
        if order:
            received_amount = float(payment_data.get('amount', 0))
            expected_amount = float(order.order_amount())
            
            # Allow small difference due to floating point
            if abs(received_amount - expected_amount) > 0.01:
                return False, f"Amount mismatch: expected {expected_amount}, got {received_amount}"
        
        return True, None
        
    except Exception as e:
        print(f"Error validating CCAvenue webhook: {e}")
        return False, str(e)


# ============================================================================
# UNIFIED WEBHOOK VERIFICATION
# ============================================================================

def get_webhook_secret_from_env(gateway_name):
    """
    Get webhook secret from environment variables
    
    Args:
        gateway_name (str): Name of the payment gateway
    
    Returns:
        str: Webhook secret or None
    """
    env_var_map = {
        'Razorpay': 'RAZORPAY_WEBHOOK_SECRET',
        'split_razorpay': 'SPLIT_RAZORPAY_WEBHOOK_SECRET'
    }
    
    env_var = env_var_map.get(gateway_name)
    if not env_var:
        return None
    
    return os.environ.get(env_var)


def verify_webhook_request(request, gateway_name):
    """
    Verify webhook request signature for Razorpay/Split Razorpay
    
    Args:
        request: Django request object
        gateway_name (str): Name of the payment gateway
    
    Returns:
        tuple: (is_valid, error_message)
    """
    # Get signature from header
    signature = request.headers.get('X-Razorpay-Signature')
    
    if not signature:
        return False, "Missing X-Razorpay-Signature header"
    
    # Get webhook secret from environment
    webhook_secret = get_webhook_secret_from_env(gateway_name)
    
    if not webhook_secret:
        print(f"WARNING: No webhook secret configured for {gateway_name}")
        print("Webhook signature verification is DISABLED")
        print("This is a SECURITY RISK in production!")
        return True, None  # Allow for backward compatibility
    
    # Get raw request body
    payload_body = request.body
    
    # Verify signature
    is_valid = verify_razorpay_webhook_signature(
        payload_body,
        signature,
        webhook_secret
    )
    
    if not is_valid:
        return False, "Invalid webhook signature"
    
    return True, None


def verify_payu_webhook(request, gateway_salt):
    """
    Verify PayU webhook hash
    
    Args:
        request: Django request object
        gateway_salt (str): Gateway salt from database
    
    Returns:
        tuple: (is_valid, error_message)
    """
    return verify_payu_webhook_hash(request.POST, gateway_salt)


def verify_phonepe_webhook(request, salt_key):
    """
    Verify PhonePe webhook signature
    
    Args:
        request: Django request object
        salt_key (str): Gateway secret (salt key)
    
    Returns:
        tuple: (is_valid, error_message)
    """
    # Get X-VERIFY header
    signature = request.headers.get('X-VERIFY')
    
    if not signature:
        print("WARNING: Missing X-VERIFY header for PhonePe webhook")
        return True, None  # Allow for backward compatibility
    
    # Get raw request body
    payload_body = request.body
    
    return verify_phonepe_webhook_signature(payload_body, signature, salt_key)
