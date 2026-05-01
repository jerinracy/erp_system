import hashlib
import hmac
import json


def generate_signature(secret, payload):
    message = json.dumps(payload, separators=(",", ":"), sort_keys=True)

    signature = hmac.new(
        key=secret.encode(), msg=message.encode(), digestmod=hashlib.sha256
    ).hexdigest()

    return signature
