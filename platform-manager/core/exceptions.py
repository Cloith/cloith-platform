class VaultError(Exception):
    """Base class for all Bitwarden/Vault related issues."""
    pass

class ItemNotFoundError(VaultError):
    """Raised when the requested item is missing from the vault."""
    pass

class InvalidItemError(VaultError):
    """Raised when the item exists but fails validation (corrupted/wrong format)."""
    pass