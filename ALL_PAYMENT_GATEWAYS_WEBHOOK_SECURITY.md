# Complete Webhook Security for ALL Payment Gateways

## Payment Gateways in Your Project

1. **Razorpay** - Uses webhook signature (HMAC-SHA256)
2. **Split Razorpay** - Uses webhook signature (HMAC-SHA256)
3. **PayU** - Uses hash verification (SHA-512)
4. **CCAvenue** - Uses encryption (AES)
5. **PhonePe** - Uses SDK verification

---

## Security Status by Gateway

| Gateway | Current Security | Needs Improvement |
|---------|-----------------|-------------------|
| Razorpay | ❌ No signature verification | ✅ Add webhook secret |
| Split Razorpay | ❌ No signature verification | ✅ Add webhook secret |
| PayU | ⚠️ Partial (verifies with API call) | ✅ Add hash verification |
| CCAvenue | ✅ Good (encrypted response) | ✅ Add additional validation |
| PhonePe | ⚠️ Partial (SDK verification) | ✅ Add signature check |

---

## What Each Gateway Needs

### 1. Razorpay & Split Razorpay
**Security Method:** Webhook Signature (HMAC-SHA256)

**What to add:**
- Webhook secret from Razorpay dashboard
- Signature verification before processing

**Implementation:** Already created in previous files

---

### 2. PayU
**Security Method:** Hash Verification (SHA-512)

**Current:** Verifies payment with API call (good!)  
**Add:** Verify incoming webhook hash

**What PayU sends:**
- `hash`: SHA-512 hash of payment data
- Formula: `sha512(salt|status||||||udf5|udf4|udf3|udf2|udf1|email|firstname|productinfo|amount|txnid|key)`

**What to verify:**
1. Calculate expected hash using gateway_salt
2. Compare with received hash
3. Only process if match

---

### 3. CCAvenue
**Security Method:** AES Encryption

**Current:** Decrypts response (good!)  
**Add:** Additional validation

**What CCAvenue sends:**
- Encrypted response (`encResp`)
- Decrypted using `working_key`

**What to verify:**
1. Decrypt response (already done ✅)
2. Validate order exists
3. Check amount matches
4. Verify order_id format

---

### 4. PhonePe
**Security Method:** SDK Verification + X-VERIFY Header

**Current:** Uses SDK to verify (good!)  
**Add:** Verify X-VERIFY header

**What PhonePe sends:**
- `X-VERIFY`: Base64(SHA256(response + salt_key + salt_index))
- Response payload

**What to verify:**
1. Extract X-VERIFY header
2. Calculate expected signature
3. Compare signatures
4. Then use SDK verification

---

## Implementation Priority

### High Priority (Critical):
1. ✅ **Razorpay** - No verification at all
2. ✅ **Split Razorpay** - No verification at all

### Medium Priority (Improve):
3. ⚠️ **PayU** - Add hash verification
4. ⚠️ **PhonePe** - Add X-VERIFY check

### Low Priority (Already Good):
5. ✅ **CCAvenue** - Already encrypted, just add validation

---

## .env Variables Needed

```bash
# Razorpay Webhook Secrets
RAZORPAY_WEBHOOK_SECRET=whsec_your_razorpay_secret
SPLIT_RAZORPAY_WEBHOOK_SECRET=whsec_your_split_secret

# PayU - Already in database (gateway_salt)
# No additional .env needed

# CCAvenue - Already in database (working_key)
# No additional .env needed

# PhonePe - Already in database (gateway_secret)
# No additional .env needed
```

---

## Summary

**Razorpay/Split Razorpay:**
- Store webhook secret in .env
- Verify HMAC-SHA256 signature
- Reject if invalid

**PayU:**
- Use existing gateway_salt from database
- Verify SHA-512 hash
- Already does API verification (good!)

**CCAvenue:**
- Use existing working_key from database
- Already decrypts (good!)
- Add order validation

**PhonePe:**
- Use existing gateway_secret from database
- Verify X-VERIFY header
- Already uses SDK (good!)

---

## Next Steps

I'll create:
1. ✅ Enhanced webhook_security.py with all gateways
2. ✅ Secure webhook views for all gateways
3. ✅ Complete implementation guide
4. ✅ Testing instructions

Ready to proceed?
