import os
import streamlit as st
from cryptography.fernet import Fernet
import hashlib

def get_encryption_key():
    """Get encryption key from environment variable"""
    key = os.getenv('ENCRYPTION_KEY')
    if not key:
        st.error("Encryption key not set!")
        st.stop()
    # Hash the key to ensure it's 32 bytes
    return hashlib.sha256(key.encode()).digest()

def init_session_state():
    """Initialize session state variables"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user_roles' not in st.session_state:
        st.session_state.user_roles = ['viewer']