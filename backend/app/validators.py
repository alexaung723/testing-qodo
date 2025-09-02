"""
Validation functions for the Qodo Demo API.
This file demonstrates input validation.
"""

import re
from typing import Any, Dict, List, Optional, Union
from datetime import datetime

# Trivial validators for demo purposes
# This file shows validation evolution
# Each function represents a small addition

def validate_email(email: str) -> bool:
    """Validate email address format."""
    # Trivial email validation for demo
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_phone(phone: str) -> bool:
    """Validate phone number format."""
    # Trivial phone validation for demo
    pattern = r'^\+?1?\d{9,15}$'
    return bool(re.match(pattern, phone))

def validate_url(url: str) -> bool:
    """Validate URL format."""
    # Trivial URL validation for demo
    pattern = r'^https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?$'
    return bool(re.match(pattern, url))

def validate_username(username: str) -> bool:
    """Validate username format."""
    # Trivial username validation for demo
    if len(username) < 3 or len(username) > 50:
        return False
    pattern = r'^[a-zA-Z0-9_-]+$'
    return bool(re.match(pattern, username))

def validate_password(password: str) -> bool:
    """Validate password strength."""
    # Trivial password validation for demo
    if len(password) < 8:
        return False
    if len(password) > 128:
        return False
    # Check for at least one uppercase, lowercase, and digit
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    return has_upper and has_lower and has_digit

def validate_integer(value: Any, min_val: Optional[int] = None, max_val: Optional[int] = None) -> bool:
    """Validate integer value within range."""
    # Trivial integer validation for demo
    try:
        int_val = int(value)
        if min_val is not None and int_val < min_val:
            return False
        if max_val is not None and int_val > max_val:
            return False
        return True
    except (ValueError, TypeError):
        return False

def validate_float(value: Any, min_val: Optional[float] = None, max_val: Optional[float] = None) -> bool:
    """Validate float value within range."""
    # Trivial float validation for demo
    try:
        float_val = float(value)
        if min_val is not None and float_val < min_val:
            return False
        if max_val is not None and float_val > max_val:
            return False
        return True
    except (ValueError, TypeError):
        return False

def validate_string(value: Any, min_length: Optional[int] = None, max_length: Optional[int] = None) -> bool:
    """Validate string value length."""
    # Trivial string validation for demo
    if not isinstance(value, str):
        return False
    if min_length is not None and len(value) < min_length:
        return False
    if max_length is not None and len(value) > max_length:
        return False
    return True

def validate_list(value: Any, min_items: Optional[int] = None, max_items: Optional[int] = None) -> bool:
    """Validate list value length."""
    # Trivial list validation for demo
    if not isinstance(value, list):
        return False
    if min_items is not None and len(value) < min_items:
        return False
    if max_items is not None and len(value) > max_items:
        return False
    return True

def validate_dict(value: Any, required_keys: Optional[List[str]] = None) -> bool:
    """Validate dictionary value and required keys."""
    # Trivial dict validation for demo
    if not isinstance(value, dict):
        return False
    if required_keys:
        for key in required_keys:
            if key not in value:
                return False
    return True

def validate_date(date_str: str, format_str: str = "%Y-%m-%d") -> bool:
    """Validate date string format."""
    # Trivial date validation for demo
    try:
        datetime.strptime(date_str, format_str)
        return True
    except ValueError:
        return False

def validate_datetime(datetime_str: str, format_str: str = "%Y-%m-%dT%H:%M:%S") -> bool:
    """Validate datetime string format."""
    # Trivial datetime validation for demo
    try:
        datetime.strptime(datetime_str, format_str)
        return True
    except ValueError:
        return False

def validate_enum(value: Any, allowed_values: List[Any]) -> bool:
    """Validate value against allowed enum values."""
    # Trivial enum validation for demo
    return value in allowed_values

def validate_regex(value: str, pattern: str) -> bool:
    """Validate string against regex pattern."""
    # Trivial regex validation for demo
    try:
        return bool(re.match(pattern, value))
    except re.error:
        return False

def validate_file_extension(filename: str, allowed_extensions: List[str]) -> bool:
    """Validate file extension."""
    # Trivial file extension validation for demo
    if not filename or '.' not in filename:
        return False
    extension = filename.lower().split('.')[-1]
    return f".{extension}" in allowed_extensions

def validate_file_size(file_size: int, max_size: int) -> bool:
    """Validate file size."""
    # Trivial file size validation for demo
    return file_size <= max_size

# Trivial helper function for demo
def validate_all(data: Dict[str, Any], rules: Dict[str, Dict[str, Any]]) -> Dict[str, List[str]]:
    """Validate multiple fields with rules."""
    errors = {}
    for field, rule in rules.items():
        if field in data:
            value = data[field]
            field_errors = []
            
            # Apply validation rules
            if 'type' in rule:
                if rule['type'] == 'int' and not validate_integer(value, rule.get('min'), rule.get('max')):
                    field_errors.append(f"Invalid integer value for {field}")
                elif rule['type'] == 'float' and not validate_float(value, rule.get('min'), rule.get('max')):
                    field_errors.append(f"Invalid float value for {field}")
                elif rule['type'] == 'string' and not validate_string(value, rule.get('min_length'), rule.get('max_length')):
                    field_errors.append(f"Invalid string value for {field}")
            
            if 'required' in rule and rule['required'] and not value:
                field_errors.append(f"{field} is required")
            
            if 'enum' in rule and not validate_enum(value, rule['enum']):
                field_errors.append(f"Invalid value for {field}")
            
            if field_errors:
                errors[field] = field_errors
    
    return errors

# Trivial comment addition for demo
# This file shows validation evolution
# Each validator represents a small addition
