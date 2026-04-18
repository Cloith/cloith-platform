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
    ITEM_MISSING = "item_missing"
    WRONG_PASSWORD = "wrong_password"
    WRONG_EMAIL = "wrong_email"
    MASTER_PASSWORD_PROMPT = "master_password_prompt"
    
    # VPS / Provider Specific
    TOKEN_MISSING = "token_missing"
    TOKEN_INVALID = "token_invalid"
    TOKEN_MODAL_PROMPT = "token_modal_prompt"
    API_ERROR = "api_error"