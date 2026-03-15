"""
SAGE Framework Configuration Module
"""

# Lazy import to avoid circular dependencies and missing dependencies at import time
def get_sage_config_loader():
    """Lazy loading function for SAGEConfigLoader"""
    from .sage_config_loader import SAGEConfigLoader
    return SAGEConfigLoader

__all__ = [
    "get_sage_config_loader",
]
