from decimal import Decimal


def sanitize_payload(data):
    """
    Convert non-JSON-serializable types (like Decimal) into safe values.
    """
    if isinstance(data, dict):
        return {key: sanitize_payload(value) for key, value in data.items()}

    if isinstance(data, list):
        return [sanitize_payload(item) for item in data]

    if isinstance(data, Decimal):
        return float(data)

    return data
