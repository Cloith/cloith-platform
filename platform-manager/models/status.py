from enum import Enum

class ResponseStatus(str, Enum):
    # Common Statuses (Shared)
    SUCCESS = "success"
    TIMEOUT = "timeout"
    NETWORK_ERROR = "network_error"
    UNKNOWN_ERROR = "unknown_error"
    CANCELLED = "cancelled"
    

    # Vault Specific
    LOCKED = "locked"
    NEED_2FA = "need_2fa"
    INVALID_OTP = "invalid_otp"
    ITEM_MISSING = "item_missing"
    WRONG_MASTER_PASSWORD = "wrong_master_password"
    WRONG_EMAIL = "wrong_email"
    INVALID_SESSION_TOKEN = "INVALID_SESSION_TOKEN"
    
    # VPS / Provider Specific
    PROVIDER_TOKEN_MISSING = "token_missing"
    PROVIDER_TOKEN_INVALID = "token_invalid"
    TOKEN_MODAL_PROMPT = "token_modal_prompt"
    PROVIDER_API_ERROR = "api_error"
    PROVIDER_RATE_LIMITED = "provider_rate_limited"
    PROVIDER_PERMISSION_DENIED = "provider_permission_denied"