import os
from typing import Optional


def get_secret(name: str, default: Optional[str] = None) -> Optional[str]:
    """
    Resolve config from environment variables first, then Streamlit secrets.
    """
    value = os.getenv(name)
    if value:
        return value

    try:
        import streamlit as st

        secret_value = st.secrets.get(name)
        if secret_value:
            return str(secret_value)
    except Exception:
        pass

    return default
