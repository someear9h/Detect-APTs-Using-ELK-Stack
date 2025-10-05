import socket
import json
from datetime import datetime
from ..config import settings


LOGSTASH_HOST = settings.LOGSTASH_HOST
LOGSTASH_PORT = settings.LOGSTASH_PORT

def send_to_logstash(event: dict):
    """Send JSON event as a single line to Logstash tcp input.


    This is a tiny, best-effort shipper for demo purposes.
    In production use Beats, Filebeat, or proper logging libraries.
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((LOGSTASH_HOST, LOGSTASH_PORT))
        payload = json.dumps(event, default=str) + "\n"
        s.sendall(payload.encode('utf-8'))
        s.close()
    except Exception as e:
        # For demo, we print; in prod, handle retry/backoff
        print(f"Failed to send to Logstash: {e}")