import hashlib
import os
import streamlit as st
from database import save_user, get_user

def hash_password(password: str) -> str:
    """Hash a password using SHA-256"""
    salt = os.getenv("SESSION_SECRET", "default_salt")
    return hashlib.sha256((password + salt).encode()).hexdigest()

def init_auth():
    """Initialize authentication system with default users"""
    # Create default demo users if they don't exist
    demo_users = [
        ("demo", "demo123"),
        ("legal_analyst", "clausewise2024"),
        ("admin", "admin123")
    ]
    
    for username, password in demo_users:
        try:
            if not get_user(username):
                password_hash = hash_password(password)
                save_user(username, password_hash)
        except Exception:
            # User already exists or other error, continue
            pass

def authenticate_user(username: str, password: str) -> bool:
    """
    Authenticate a user with username and password
    
    Args:
        username: User's username
        password: User's password
        
    Returns:
        bool: True if authentication successful, False otherwise
    """
    if not username or not password:
        return False
    
    user = get_user(username)
    if not user:
        return False
    
    password_hash = hash_password(password)
    return user['password_hash'] == password_hash

def logout_user():
    """Log out the current user"""
    st.session_state.authenticated = False
    st.session_state.current_user = None
    st.rerun()

def require_auth(func):
    """Decorator to require authentication for a function"""
    def wrapper(*args, **kwargs):
        if not st.session_state.get('authenticated', False):
            st.error("Authentication required")
            return None
        return func(*args, **kwargs)
    return wrapper

def get_current_user() -> str:
    """Get the currently authenticated user"""
    return st.session_state.get('current_user', 'Anonymous')

def is_authenticated() -> bool:
    """Check if user is currently authenticated"""
    return st.session_state.get('authenticated', False)
