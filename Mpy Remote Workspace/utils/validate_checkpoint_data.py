def validate_checkpoint_data(data):
    required_fields = {
        'name': str,
        'gpio': int,
        'potl': bool,
        'chrono': str,
    }

    for field, field_type in required_fields.items():
        if field not in data:
            return False, f"Missing required field: {field}"
        if not isinstance(data[field], field_type):
            return False, f"Incorrect type for field: {field}. Expected {field_type.__name__}."

    # Additional validation for specific fields
    if len(data['chrono']) != 8 or not data['chrono'].count(':') == 2:
        return False, "Invalid format for field: chrono. Expected format HH:MM:SS."

    return True, "Validation successful"